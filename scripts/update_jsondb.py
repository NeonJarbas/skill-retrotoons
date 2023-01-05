from youtube_archivist import YoutubeMonitor
import shutil
import json
from os.path import dirname, isfile

url = "https://www.youtube.com/channel/UCfeIkx_3ajdIvFtsHWduThg"
archive = YoutubeMonitor(db_name="RetroToons",
                                      min_duration=30 * 60,

                                      blacklisted_kwords=["trailer", "teaser", "movie scene",
                                                          "movie clip", "behind the scenes",
                                                          "Movie Preview", "soundtrack",
                                                          "beverly hillbillies", "petticoat",
                                                          "east side kids", "dusty's trail",
                                                          "the cisco kid", "newsreel", "fury",
                                                          "dragnet", "documentary",
                                                          "groucho", "mickey rooney", "lucy show",
                                                          " OST", "opening theme"])

# load previous cache
cache_file = f"{dirname(dirname(__file__))}/bootstrap.json"
if isfile(cache_file):
    try:
        with open(cache_file) as f:
            data = json.load(f)
            archive.db.update(data)
            archive.db.store()
    except:
        pass  # corrupted for some reason

    shutil.rmtree(cache_file, ignore_errors=True)


# parse new vids
archive.parse_videos(url)

# save bootstrap cache
shutil.copy(archive.db.path, cache_file)
