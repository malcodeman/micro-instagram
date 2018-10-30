import requests
import os
from timeit import default_timer as timer


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
    headers = os.environ['COOKIE']
    params = f'query_hash={query_id}&variables={{"id": "{channel_id}", "first": 12, "after": "{end_cursor}"}}'
    result = requests.get(
        f'https://www.instagram.com/graphql/query/?{params}',  headers=headers)
    return result.json()


def parse_posts_list(posts):
    posts_list = []
    for post in posts:
        posts_list.append({
            "pic_url": post["node"]["display_url"]
        })
    return posts_list


def get_has_next_page(content):
    return content["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]


def get_end_cursor(content):
    return content["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]


def get_edges(content):
    return content["data"]["user"]["edge_owner_to_timeline_media"]["edges"]


def get_posts(json_content, query_id):
    start = timer()
    print(f"get_posts start: {start}")
    posts = parse_posts_list(
        json_content["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"])
    next_page = json_content["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
    if(next_page):
        channel_id = json_content["graphql"]["user"]["id"]
        end_cursor = json_content["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
        next_page = get_next_page(channel_id, query_id, end_cursor)
        posts_all = parse_posts_list(get_edges(next_page))
        has_next_page = get_has_next_page(next_page)
        while has_next_page:
            end_cursor = get_end_cursor(next_page)
            next_page = get_next_page(channel_id, query_id, end_cursor)
            posts_all += parse_posts_list(get_edges(next_page))
            has_next_page = get_has_next_page(next_page)
        posts += posts_all
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
    json_content = scrap_page(
        "https://www.instagram.com/" + str(user) + "/?__a=1")
    response = {
        "user": get_user_info(json_content),
        "posts": get_posts(json_content, query_id)
    }
    return response
