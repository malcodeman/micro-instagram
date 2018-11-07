import requests
import os
from timeit import default_timer as timer
from flask import request
import pathlib


def get_auth_header():
    return {
        "Cookie": request.headers["Authorization"]
    }


def scrap_page(page):
    headers = get_auth_header()
    result = requests.get(page, headers=headers)
    return result.json()


def find_nth(string, sub, n):
    start = string.find(sub)
    while start >= 0 and n > 1:
        start = string.find(sub, start+len(sub))
        n -= 1
    return start


def get_query_id():
    start = timer()
    print(f"get_query_id start: {start}")
    url = "https://www.instagram.com/static/bundles/base/ProfilePageContainer.js/1ead5e8e1146.js"
    string = scrap_js(url)
    index = find_nth(string, "queryId", 3) + 9
    queryId = string[index:index + 32]
    end = timer()
    print(f"get_query_id end: {end}\n")
    print(f"completed in {end - start} seconds")
    return queryId


def scrap_js(page_url):
    result = requests.get(page_url)
    return result.text


def get_next_page(channel_id, query_id, end_cursor):
    headers = get_auth_header()
    params = f'query_hash={query_id}&variables={{"id": "{channel_id}", "first": 12, "after": "{end_cursor}"}}'
    result = requests.get(
        f'https://www.instagram.com/graphql/query/?{params}',  headers=headers)
    return result.json()


def parse_caption(caption):
    if len(caption) > 0:
        return caption[0]["node"]["text"]
    return None


def download_image(id, url):
    extension = pathlib.Path(url).suffix
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"/Users/username/Desktop/images/{id}{extension}", 'wb') as f:
            f.write(response.content)


def parse_posts_list(posts):
    posts_list = []
    for index, post in enumerate(posts):
        posts_list.append({
            "caption": parse_caption(post["node"]["edge_media_to_caption"]["edges"]),
            "comments_count": post["node"]["edge_media_to_comment"]["count"],
            "id": post["node"]["id"],
            "is_video": post["node"]["is_video"],
            "likes_count": post["node"]["edge_media_preview_like"]["count"],
            "pic_url": post["node"]["display_url"],
            "post_url": f'https://www.instagram.com/p/{post["node"]["shortcode"]}',
            "taken_at": post["node"]["taken_at_timestamp"],
        })
        if posts_list[index]["is_video"]:
            shortcode = post["node"]["shortcode"]
            json_content = scrap_page(
                "https://www.instagram.com/p/" + str(shortcode) + "/?__a=1")
            video_url = json_content["graphql"]["shortcode_media"]["video_url"]
            video_view_count = json_content["graphql"]["shortcode_media"]["video_view_count"]
            posts_list[index].update(
                {"video_url": video_url, "video_view_count": video_view_count})
        #download_image(posts_list[index]["id"], posts_list[index]["pic_url"])
    return posts_list


def get_has_next_page(content):
    return content["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]


def get_end_cursor(content):
    return content["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]


def get_edges(content):
    return content["data"]["user"]["edge_owner_to_timeline_media"]["edges"]


def get_all_posts(channel_id, query_id, end_cursor, next_page, posts_all, has_next_page):
    if has_next_page == False:
        return posts_all
    next_page = get_next_page(channel_id, query_id, end_cursor)
    end_cursor = get_end_cursor(next_page)
    posts_all += parse_posts_list(get_edges(next_page))
    has_next_page = get_has_next_page(next_page)
    return get_all_posts(channel_id, query_id, end_cursor, next_page, posts_all, has_next_page)


def get_posts(latest_posts, query_id):
    start = timer()
    print(f"get_posts start: {start}")
    posts = parse_posts_list(
        latest_posts["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"])
    has_next_page = latest_posts["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
    channel_id = latest_posts["graphql"]["user"]["id"]
    end_cursor = latest_posts["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
    posts += get_all_posts(channel_id, query_id, end_cursor,
                           latest_posts, [], has_next_page)
    end = timer()
    print(f"get_posts end: {end}\n")
    print(f"completed in {end - start} seconds")
    return posts


def get_user_info(json_content):
    user = {
        "biography": json_content["graphql"]["user"]["biography"],
        "posts": json_content["graphql"]["user"]["edge_owner_to_timeline_media"]["count"],
        "followers": json_content["graphql"]["user"]["edge_followed_by"]["count"],
        "following": json_content["graphql"]["user"]["edge_follow"]["count"],
    }
    return user


def get_user(user):
    query_id = get_query_id()
    latest_posts = scrap_page(
        "https://www.instagram.com/" + str(user) + "/?__a=1")
    response = {
        "user": get_user_info(latest_posts),
        "posts": get_posts(latest_posts, query_id)
    }
    return response
