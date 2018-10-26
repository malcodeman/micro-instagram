import requests
import os


def scrap_page(page):
    headers = {"Cookie": os.environ['COOKIE']}
    result = requests.get(page, headers=headers)
    return result.json()


def get_user_info(json_content):
    user = {
        "biography": json_content["graphql"]["user"]["biography"],
        "posts": json_content["graphql"]["user"]["edge_owner_to_timeline_media"]["count"],
        "followers": json_content["graphql"]["user"]["edge_followed_by"]["count"],
        "following": json_content["graphql"]["user"]["edge_follow"]["count"],
    }
    return user


def get_user(user):
    json_content = scrap_page(
        "https://www.instagram.com/" + str(user) + "/?__a=1")
    response = {
        "user": get_user_info(json_content)
    }
    return response
