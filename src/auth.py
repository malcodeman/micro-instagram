import requests


def get_csrf_token():
    url = "https://www.instagram.com/accounts/login/?__a=1"
    res = requests.get(url)
    csrftoken = res.cookies["csrftoken"]
    return csrftoken


def get_cookie(cookies):
    csrftoken = cookies["csrftoken"]
    ds_user_id = cookies["ds_user_id"]
    rur = cookies["rur"]
    sessionid = cookies["sessionid"]
    shbid = cookies["shbid"]
    shbts = cookies["shbts"]
    return f"csrftoken={csrftoken}; ds_user_id={ds_user_id};rur={rur}; sessionid={sessionid}; shbid={shbid}; shbts={shbts}"


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
    
    res_cookie = {
        "Cookie": get_cookie(req.cookies)
    }
    return res_cookie
