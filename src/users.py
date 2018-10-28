import requests
import os


def scrap_page(page):
    headers = os.environ['COOKIE']
    result = requests.get(page, headers=headers)
    return result.json()


def find_nth(string, sub, n):
    start = string.find(sub)
    while start >= 0 and n > 1:
        start = string.find(sub, start+len(sub))
        n -= 1
    return start


def get_query_id():
    url = "https://www.instagram.com/static/bundles/base/ProfilePageContainer.js/1ead5e8e1146.js"
    string = scrap_js(url)
    index = find_nth(string, "queryId", 3) + 9
    queryId = string[index:index + 32]
    return queryId


def scrap_js(page_url):
    result = requests.get(page_url)
    return result.text


def get_next_page(channel_id, query_id, end_cursor):
    headers = os.environ['COOKIE']
    params = f'query_hash={query_id}&variables={{"id": "{channel_id}", "first": 12, "after": "{end_cursor}"}}'
    result = requests.get(
        f'https://www.instagram.com/graphql/query/?{params}',  headers=headers)
    return result.json()


def get_posts_next(json_content):
    content = json_content["data"]["user"]["edge_owner_to_timeline_media"]
    posts_array = []
    for post in content["edges"]:
        posts_array.append({
            "pic_url": post["node"]["display_url"]
        })
    return posts_array


def get_posts(json_content, query_id):
    content = json_content["graphql"]["user"]["edge_owner_to_timeline_media"]
    next_page = content["page_info"]["has_next_page"]
    end_cursor = content["page_info"]["end_cursor"]
    channel_id = json_content["graphql"]["user"]["id"]
    posts_latest = []
    for post in content["edges"]:
        posts_latest.append({
            "pic_url": post["node"]["display_url"]
        })
    posts_next = get_posts_next(
        get_next_page(channel_id, query_id, end_cursor))
    merged_posts = posts_latest + posts_next
    return merged_posts


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
    json_content = scrap_page(
        "https://www.instagram.com/" + str(user) + "/?__a=1")
    response = {
        "user": get_user_info(json_content),
        "posts": get_posts(json_content, query_id)
    }
    return response
