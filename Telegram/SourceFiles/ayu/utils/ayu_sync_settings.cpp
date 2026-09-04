// This is the source code of AyuGram for Desktop.
//
// We do not and cannot prevent the use of our code,
// but be respectful and credit the original author.
//
// Copyright @Radolyn, 2026
#include "ayu/utils/ayu_sync_settings.h"

#include "apiwrap.h"
#include "ayu/ayu_settings.h"
#include "ayu/libs/json.hpp"
#include "data/data_session.h"
#include "data/data_user.h"
#include "history/history.h"
#include "ui/toast/toast.h"
#include "history/history_item.h"
#include "main/main_session.h"
#include "mtproto/sender.h"
#include "api/api_common.h"

namespace AyuSettingsSync {

namespace {

void ParseMessage(const QString &text) {
	const auto tag = QString("#ayugram_settings");
	if (!text.contains(tag)) {
		return;
	}

	auto startIndex = text.indexOf('{');
	auto endIndex = text.lastIndexOf('}');
	if (startIndex == -1 || endIndex == -1 || endIndex <= startIndex) {
		return;
	}

	auto jsonText = text.mid(startIndex, endIndex - startIndex + 1);

	try {
		auto j = nlohmann::json::parse(jsonText.toStdString());
		if (j.contains("link_previews") && j["link_previews"].is_object()) {
			std::unordered_map<QString, QString> map;
			for (auto& [key, value] : j["link_previews"].items()) {
				if (value.is_string()) {
					map[QString::fromStdString(key)] = QString::fromStdString(value.get<std::string>());
				}
			}
			AyuSettings::getInstance().setDynamicLinkPreviews(map);
		}
		if (j.contains("instant_view") && j["instant_view"].is_object()) {
			std::unordered_map<QString, QString> map;
			for (auto& [key, value] : j["instant_view"].items()) {
				if (value.is_string()) {
					map[QString::fromStdString(key)] = QString::fromStdString(value.get<std::string>());
				}
			}
			AyuSettings::getInstance().setDynamicInstantView(map);
		}
		Ui::Toast::Show("AyuGram settings updated!");
	} catch (...) {
		// Ignore parsing errors
	}
}

} // namespace

void Start(Main::Session* session) {
	if (!session) return;
	session->api().request(MTPmessages_Search(
		MTP_flags(0),
		MTP_inputPeerSelf(), // Fix: Always use inputPeerSelf for Saved Messages to avoid PEER_ID_INVALID on startup
		MTP_string("#ayugram_settings"),
		MTP_inputPeerEmpty(),
		MTP_inputPeerEmpty(),
		MTPVector<MTPReaction>(),
		MTP_int(0), // top_msg_id
		MTP_inputMessagesFilterEmpty(),
		MTP_int(0), // min_date
		MTP_int(0), // max_date
		MTP_int(0), // offset_id
		MTP_int(0), // add_offset
		MTP_int(1), // limit
		MTP_int(0), // max_id
		MTP_int(0), // min_id
		MTP_long(0) // hash
	)).done([=](const MTPmessages_Messages &result) {
		result.match([&](const auto &data) {
			if constexpr (requires { data.vmessages(); }) {
				if (!data.vmessages().v.isEmpty()) {
					const auto &msg = data.vmessages().v.front();
					if (msg.type() == mtpc_message) {
						ParseMessage(qs(msg.c_message().vmessage()));
					}
				}
			}
		});
	}).fail([=](const MTP::Error &error) {
		Ui::Toast::Show("AyuGram settings sync failed: " + error.type());

	}).send();

	rpl::merge(
		session->data().newItemAdded(),
		session->data().itemDataChanges()
	) | rpl::on_next([=](not_null<HistoryItem*> item) {
		if (item->history()->peer->isSelf()) {
			if (item->originalText().text.contains("#ayugram_settings")) {
				ParseMessage(item->originalText().text);
			}
		}
	}, session->lifetime());
}

} // namespace AyuSettingsSync
