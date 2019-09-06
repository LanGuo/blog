import boto3
import glob

from chalicelib import dao, podcast, renderer

fname = "rss.xml"
bucket_name = "dataskeptic.com"
db_s3_key = "posts.db.json"

s3 = boto3.resource('s3')

#mode = 'reload_rss'
mode = 'reload_all'
#mode = 'delete'
mode = 'reload_one'
#mode = 'update'

filepath = "episodes/2019/facebook-negotiating-bots-Invented-a-language.md"

database = dao.get_database(s3, bucket_name, db_s3_key)

if mode == 'reload_rss':
	url = 'http://dataskeptic.libsyn.com/rss'
	print(f'fetching {url}')
	podcast.update_podcast_rss(database, s3, bucket_name, db_s3_key, url)
elif mode == 'reload_one':
	repo = "data-skeptic/blog"
	branch = "/master"
	author = "kyle@dataskeptic.com"
	renderer.render_one(database, s3, bucket_name, repo, branch, filepath, author)
elif mode == 'reload_all':
	repo = "data-skeptic/blog"
	branch = "/master"
	author = "kyle@dataskeptic.com"
	posts = glob.glob("**/**/*.md")
	posts.extend(glob.glob("**/**/*.ipynb"))
	#posts.extend(glob.glob("**/**/*.Rmd"))
	for post in posts:
		renderer.render_one(database, s3, bucket_name, repo, branch, post, author)
elif mode == 'update':
	dao.update_database(s3, bucket_name, db_s3_key, database)
elif mode == 'delete':
	filepath = 'episodes/2019/___aaron.md'
	s3key = renderer.get_rendered_key_name(filepath)
	doc_type = 'md'
	renderer.remove(s3, bucket_name, db_s3_key, database, doc_type, s3key)
else:
	raise Exception(f"Unknown mode: {mode}")

#updated = podcast.update_podcast_from_file(s3, database, fname)
#print(updated)
#if updated:
#    print("Podcast updates made")
#    podcast.update_database(s3, bucket_name, db_s3_key, database)