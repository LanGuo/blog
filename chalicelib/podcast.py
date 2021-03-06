import botocore
import pandas as pd
import requests
import xmltodict

from . import dao

def update_podcast_rss(database, s3, bucket_name, db_s3_key, url):
    download = False
    fname = "podcast.rss"
    if download:
        r = requests.get(url)
        f = open(fname, 'wb')
        f.write(r.text.encode('utf-8'))
        f.close()
    dao.get_database(s3, bucket_name, db_s3_key, prefix="blog/")
    updated = update_podcast_from_file(s3, database, fname)
    if updated:
        print("Podcast updates made")
        for url in updated:
            dao.update_database(s3, bucket_name, db_s3_key, database, url)


def update_podcast_from_file(s3, database, fname):
    updated = []
    with open(fname) as fd:
        xml = xmltodict.parse(fd.read())
        episodes = xml['rss']['channel']['item']
        n = len(episodes)
        print('Number of episodes: {n}'.format(n=n))
        for episode in episodes:
            result = update_episode(database, episode)
            updated.extend(result)
    return updated


def requires_update(ep, guid, duration):
    if 'guid' not in ep:
        return True
    if 'duration' not in ep:
        return True
    if ep['guid'] != guid:
        return True
    if ep['duration'] != duration:
        return True
    return False



#/episodes/2019/the-death-of-a-language


def update_episode(database, episode):
    guid = episode['guid']['#text']
    url = episode['enclosure']['@url']
    link = episode['link']
    duration = episode['itunes:duration'] # format: 03:56
    prettyname = link.replace("http://dataskeptic.com", "").replace("https://dataskeptic.com", "")
    if prettyname in database:
        ep = database[prettyname]
        if requires_update(ep, guid, duration):
            ep['duration'] = duration
            ep['guid'] = guid
            # TODO: related content (media, guest, etc)
            database[prettyname] = ep
            return [prettyname]
        else:
            return []
    else:
        # TODO: if episode is more than N minutes old, email Kyle once
        print("********************* --- WTF is {prettyname}".format(prettyname=prettyname))
        return []

