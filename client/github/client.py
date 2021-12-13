import base64
import os
from urllib.parse import urljoin
from datetime import datetime, timedelta

import requests


class GithubClient:
    GITHUB_CLIENT_URL = "https://api.github.com"

    def __init__(self):
        username = "glennren"
        access_token = os.environ["GITHUB_ACCESS_TOKEN"]

        auth = f"{username}:{access_token}"
        auth_bytes = auth.encode("ascii")
        auth_base64 = base64.b64encode(auth_bytes).decode("ascii")

        self.AUTH = f"Basic {auth_base64}"

    def _get_request(self, url_segment: str, start: datetime = None, end: datetime = None):
        url = urljoin(self.GITHUB_CLIENT_URL, url_segment)

        headers = {
            "Authorization": self.AUTH,
        }

        if end is None:
            end = datetime.now() # today

        if start is None:
            start = end - timedelta(1) # yesterday

        # params = {
        #     "since": "2021-06-09T05:00:00-04:56", # start
        #     "until": "2021-06-10T05:00:00-04:56", # end
        # }
        params = {
            "since": start,
            "until": end,
        }

        response = requests.get(url, headers=headers, params=params)

        return response

    def get_repo_commits(self):
        return self._get_request(
            url_segment="/repos/sumatokado/suma-core/commits"
        ).json()

    def get_commit(self, commit_hash: str):
        return self._get_request(
            url_segment=f"/repos/sumatokado/suma-core/commits/{commit_hash}"
        ).json()
