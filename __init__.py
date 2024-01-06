import random
from os.path import join, dirname

import requests
from json_database import JsonStorageXDG

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class RetroToonsSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        self.supported_media = [MediaType.CARTOON]
        self.skill_icon = self.default_bg = join(dirname(__file__), "ui", "retrotoons_icon.jpg")
        self.archive = JsonStorageXDG("RetroToons", subfolder="OCP")
        super().__init__(*args, **kwargs)

    def initialize(self):
        self._sync_db()
        self.load_ocp_keywords()

    def _sync_db(self):
        bootstrap = "https://github.com/JarbasSkills/skill-retrotoons/raw/dev/bootstrap.json"
        data = requests.get(bootstrap).json()
        self.archive.merge(data)
        self.schedule_event(self._sync_db, random.randint(3600, 24 * 3600))

    def load_ocp_keywords(self):
        titles = []

        for url, data in self.archive.items():
            t = data["title"].split("|")[0].split("-")[0].split("1 Hour")[0].strip()
            titles.append(t)

        self.register_ocp_keyword(MediaType.CARTOON,
                                  "cartoon_name", titles)
        self.register_ocp_keyword(MediaType.CARTOON,
                                  "cartoon_streaming_provider",
                                  ["RetroToons", "RetroToon", "Retro Toon"])

    def get_playlist(self, score=50, num_entries=25):
        pl = self.featured_media()[:num_entries]
        return {
            "match_confidence": score,
            "media_type": MediaType.CARTOON,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "bg_image": self.default_bg,
            "title": "Retro Toons (Cartoon Playlist)",
            "author": "Retro Toons"
        }

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = 25 if media_type == MediaType.CARTOON else 0
        entities = self.ocp_voc_match(phrase)
        base_score += 30 * len(entities)

        title = entities.get("cartoon_name")
        skill = "cartoon_streaming_provider" in entities  # skill matched

        if skill:
            yield self.get_playlist(base_score)

        if title:
            candidates = [video for video in self.archive.values()
                          if title.lower() in video["title"].lower()]

            for video in candidates:
                yield {
                    "title": video["title"],
                    "artist": video["author"],
                    "match_confidence": min(100, base_score),
                    "media_type": MediaType.CARTOON,
                    "uri": "youtube//" + video["url"],
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["thumbnail"],
                    "bg_image": video["thumbnail"],
                }

    @ocp_featured_media()
    def featured_media(self):
        return [{
            "title": video["title"],
            "image": video["thumbnail"],
            "match_confidence": 70,
            "media_type": MediaType.CARTOON,
            "uri": "youtube//" + video["url"],
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "bg_image": video["thumbnail"],
            "skill_id": self.skill_id
        } for video in self.archive.values()]


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = RetroToonsSkill(bus=FakeBus(), skill_id="t.fake")

    for r in s.search_db("play superman", MediaType.CARTOON):
        print(r)
        # {'title': 'SUPERMAN | Original Series 1 Hour Collection', 'artist': 'Retro Toons', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=3lFHN3TQYQg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/3lFHN3TQYQg/sddefault.jpg', 'bg_image': 'https://i.ytimg.com/vi/3lFHN3TQYQg/sddefault.jpg'}

    for r in s.search_db("play RetroToons", MediaType.CARTOON):
        print(r)
        # {'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'playlist': [{'title': 'WACKY AND PACKY | Original Season 1', 'image': 'https://i.ytimg.com/vi/JHMrJwVTKIE/sddefault.jpg', 'match_confidence': 70, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=JHMrJwVTKIE', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'bg_image': 'https://i.ytimg.com/vi/JHMrJwVTKIE/sddefault.jpg', 'skill_id': 't.fake'}, {'title': 'SUPERMAN | Original Series 1 Hour Collection', 'image': 'https://i.ytimg.com/vi/3lFHN3TQYQg/sddefault.jpg', 'match_confidence': 70, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=3lFHN3TQYQg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'bg_image': 'https://i.ytimg.com/vi/3lFHN3TQYQg/sddefault.jpg', 'skill_id': 't.fake'}, {'title': 'POPEYE THE SAILOR MAN | 1 Hour Classic Collection', 'image': 'https://i.ytimg.com/vi/mlg2VJj837U/sddefault.jpg', 'match_confidence': 70, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=mlg2VJj837U', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'bg_image': 'https://i.ytimg.com/vi/mlg2VJj837U/sddefault.jpg', 'skill_id': 't.fake'}, {'title': 'Felix The Cat 1 Hour Collection', 'image': 'https://i.ytimg.com/vi/5MbAadgPC08/sddefault.jpg', 'match_confidence': 70, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=5MbAadgPC08', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'bg_image': 'https://i.ytimg.com/vi/5MbAadgPC08/sddefault.jpg', 'skill_id': 't.fake'}, {'title': 'Popeye The Sailor Man - Collection #5', 'image': 'https://i.ytimg.com/vi/KF32SvUyUEo/sddefault.jpg', 'match_confidence': 70, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=KF32SvUyUEo', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'bg_image': 'https://i.ytimg.com/vi/KF32SvUyUEo/sddefault.jpg', 'skill_id': 't.fake'}, {'title': 'Popeye The Sailor Man - Collection #3', 'image': 'https://i.ytimg.com/vi/t74jr4kvhbA/sddefault.jpg', 'match_confidence': 70, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=t74jr4kvhbA', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'bg_image': 'https://i.ytimg.com/vi/t74jr4kvhbA/sddefault.jpg', 'skill_id': 't.fake'}, {'title': 'Popeye The Sailor Man - Classic Collection #2', 'image': 'https://i.ytimg.com/vi/J8cTXmywlyw/sddefault.jpg', 'match_confidence': 70, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'youtube//https://youtube.com/watch?v=J8cTXmywlyw', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'bg_image': 'https://i.ytimg.com/vi/J8cTXmywlyw/sddefault.jpg', 'skill_id': 't.fake'}], 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'bg_image': '/home/miro/PycharmProjects/OCP_sprint/skills/skill-retrotoons/ui/retrotoons_icon.jpg', 'title': 'Retro Toons (Cartoon Playlist)', 'author': 'Retro Toons'}

