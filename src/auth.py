import requests


def get_csrf_token():
    url = "https://www.instagram.com/accounts/login/?__a=1"
    res = requests.get(url)
    csrftoken = res.cookies["csrftoken"]
    return csrftoken


def login(username, password):
    csrftoken = get_csrf_token()
    headers = {
        "X-CSRFToken": csrftoken,
        'Cookie': f'csrftoken={csrftoken}'
    }
    data = {
        "username": username,
        "password": password
    }
    url = "https://www.instagram.com/accounts/login/ajax/"
    req = requests.post(url, headers=headers, data=data)
    res_cookies = {
        "sessionid": req.cookies["sessionid"],
        "shbts": req.cookies["shbts"],
        "shbid": req.cookies["shbid"],
        "ds_user_id": req.cookies["ds_user_id"],
        "csrftoken": req.cookies["csrftoken"],
        "mcd": req.cookies["mcd"],
        "rur": req.cookies["rur"],
    }
    return res_cookies
