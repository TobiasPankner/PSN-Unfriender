import json
import re
from urllib.parse import parse_qs
from urllib.parse import urlparse

import requests
from tqdm import tqdm


def obtain_auth_code(npsso_token):
    url = "https://ca.account.sony.com/api/authz/v3/oauth/authorize"
    headers = {
        "Cookie": f"npsso={npsso_token}"
    }
    params = {
        "access_type": "offline",
        "client_id": "09515159-7237-4370-9b40-3806e67c0891",
        "scope": "psn:mobile.v2.core psn:clientapp",
        "redirect_uri": "com.scee.psxandroid.scecompcall://redirect",
        "response_type": "code",
    }
    response = requests.get(
        url,
        headers=headers,
        params=params,
        allow_redirects=False,
    )
    response.raise_for_status()

    location_url = response.headers["location"]
    parsed_url = urlparse(location_url)
    parsed_qs = parse_qs(parsed_url.query)

    code = parsed_qs['code'][0]
    return code


def obtain_auth_jwt(code):
    url = "https://ca.account.sony.com/api/authz/v3/oauth/token"
    body = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "com.scee.psxandroid.scecompcall://redirect",
        "scope": "psn:mobile.v2.core psn:clientapp",
        "token_format": "jwt",
    }
    headers = {
        "Authorization": "Basic MDk1MTUxNTktNzIzNy00MzcwLTliNDAtMzgwNmU2N2MwODkxOnVjUGprYTV0bnRCMktxc1A="
    }
    response = requests.post(
        url,
        headers=headers,
        data=body
    )
    response.raise_for_status()

    auth_resp_json = response.json()
    return auth_resp_json["access_token"]


def authenticate_with_npsso_token(npsso_token):
    code = obtain_auth_code(npsso_token)
    access_token = obtain_auth_jwt(code)
    return access_token


def get_friend_list(jwt_token):
    url = "https://m.np.playstation.com/api/userProfile/v1/internal/users/me/friends"
    params = {
        "limit": 1000
    }
    headers = {
        "Content-Type": "application/json",
        "accept-language": "en-US",
        "user-agent": "okhttp/4.9.2",
        "Authorization": f"Bearer {jwt_token}"
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    response_json = response.json()
    return response_json['friends']


def profile_ids_to_names_chunked(jwt_token, profile_ids, start=0):
    url = "https://m.np.playstation.com/api/userProfile/v1/internal/users/profiles"
    params = {
        "accountIds": ",".join(profile_ids[start:start + 100])
    }
    headers = {
        "Content-Type": "application/json",
        "accept-language": "en-US",
        "user-agent": "okhttp/4.9.2",
        "Authorization": f"Bearer {jwt_token}"
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    response_json = response.json()
    return response_json['profiles']


def profile_ids_to_names(jwt_token, profile_ids):
    to_return = []

    chunk_size = 100
    num_chunks = len(profile_ids) // chunk_size

    for i in range(num_chunks + 1):
        start_index = i * chunk_size

        to_return.extend(profile_ids_to_names_chunked(jwt_token, profile_ids, start_index))
    return to_return


def remove_friend(jwt_token, profile_id):
    url = f"https://m.np.playstation.com/api/userProfile/v1/internal/users/me/friends/{profile_id}"
    headers = {
        "Content-Type": "application/json",
        "accept-language": "en-US",
        "user-agent": "okhttp/4.9.2",
        "Authorization": f"Bearer {jwt_token}"
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def is_name_whitelisted(patterns, name):
    for pattern in patterns:
        if re.match(pattern, name):
            return True
    return False


if __name__ == '__main__':
    try:
        with open("configuration.json", 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print("configuration.json file not found. Did you forget to rename the example file?")
        exit(1)

    auth = authenticate_with_npsso_token(config['npsso_token'])

    friend_ids = get_friend_list(auth)

    print(f"Found {len(friend_ids)} friends")

    profiles = profile_ids_to_names(auth, friend_ids)
    names = [p['onlineId'] for p in profiles]

    friends_zip = zip(friend_ids, names)
    friend_ids_with_onlineIds = list(friends_zip)

    to_remove = []
    to_keep = []

    for friend in friend_ids_with_onlineIds:
        friend_id, friend_name = friend

        if is_name_whitelisted(config['nameWhitelistPatterns'], friend_name):
            to_keep.append(friend)
        else:
            to_remove.append(friend)

    print(f"\nFriends to remove ({len(to_remove)}): ")
    print('\n'.join([p[1] for p in to_remove]))

    print(f"\nFriends to keep ({len(to_keep)}): ")
    print('\n'.join([p[1] for p in to_keep]))

    if input("\nValidate the output above. Continue? (y/n)") != "y":
        exit(1)

    print(f"\nRemoving {len(to_remove)} friends...")
    for friend in tqdm(to_remove[:5]):
        friend_id = friend[0]
        remove_friend(auth, friend_id)
