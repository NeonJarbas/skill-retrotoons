from os.path import join, dirname

from ovos_plugin_common_play.ocp import MediaType, PlaybackType
from ovos_utils.log import LOG
from ovos_utils.parse import fuzzy_match
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    ocp_search, ocp_featured_media
from youtube_archivist import YoutubeMonitor


class RetroToonsSkill(OVOSCommonPlaybackSkill):
    def __init__(self):
        super().__init__("RetroToons")
        self.supported_media = [MediaType.CARTOON,
                                MediaType.GENERIC]
        self.skill_icon = self.default_bg = join(dirname(__file__), "ui", "retrotoons_icon.jpg")
        self.archive = YoutubeMonitor(db_name="RetroToons",
                                      min_duration=30 * 60,
                                      logger=LOG,
                                      blacklisted_kwords=["trailer", "teaser", "movie scene",
                                                          "movie clip", "behind the scenes",
                                                          "Movie Preview", "soundtrack",
                                                          "beverly hillbillies", "petticoat",
                                                          "east side kids", "dusty's trail",
                                                          "the cisco kid", "newsreel", "fury",
                                                          "dragnet", "documentary",
                                                          "groucho", "mickey rooney", "lucy show",
                                                          " OST", "opening theme"])

    def initialize(self):
        url = "https://www.youtube.com/channel/UCfeIkx_3ajdIvFtsHWduThg"
        self.archive.monitor(url)
        self.archive.setDaemon(True)
        self.archive.start()

    # matching
    def match_skill(self, phrase, media_type):
        score = 0
        if self.voc_match(phrase, "movie") or media_type == MediaType.CARTOON:
            score += 10
        if self.voc_match(phrase, "raven"):
            score += 50
        return score

    def normalize_title(self, title):
        title = title.lower().strip()
        title = self.remove_voc(title, "raven")
        title = self.remove_voc(title, "movie")
        title = title.replace("|", "").replace('"', "") \
            .replace(':', "").replace('”', "").replace('“', "") \
            .strip()
        return " ".join(
            [w for w in title.split(" ") if w])  # remove extra spaces

    def calc_score(self, phrase, match, base_score=0):
        score = base_score
        score += 100 * fuzzy_match(phrase.lower(), match["title"].lower())
        return min(100, score)

    def get_playlist(self, score=50, num_entries=250):
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
        base_score = self.match_skill(phrase, media_type)
        if self.voc_match(phrase, "retrotoons"):
            yield self.get_playlist(base_score)
        if media_type == MediaType.CARTOON:
            # only search db if user explicitly requested movies
            phrase = self.normalize_title(phrase)
            for url, video in self.archive.db.items():
                yield {
                    "title": video["title"],
                    "author": "Full Free Films",
                    "match_confidence": self.calc_score(phrase, video, base_score),
                    "media_type": MediaType.CARTOON,
                    "uri": "youtube//" + url,
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["thumbnail"],
                    "bg_image": self.default_bg
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
        } for video in self.archive.sorted_entries()]


def create_skill():
    return RetroToonsSkill()
