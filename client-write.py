import base64
import os
import requests

from urllib.parse import urljoin
from typing import Any, Dict, NamedTuple

class PersonalAccount(NamedTuple):
    username: str
    access_token: str


WORK_TO_PERSONAL = {
    "glenn_ramp": PersonalAccount(
        username="GlennRen",
        access_token=os.environ["GLENN_PERSONAL_ACCESS_TOKEN"]
    ),
}


class GithubWriteClient:
    GITHUB_CLIENT_URL = "https://api.github.com"

    def __init__(self):
        personal_account = WORK_TO_PERSONAL["glenn_ramp"]

        auth = f"{personal_account.username}:{personal_account.access_token}"
        auth_bytes = auth.encode("ascii")
        auth_base64 = base64.b64encode(auth_bytes).decode("ascii")

        self.AUTH = f"Basic {auth_base64}"

    def _get_request(self, url_segment: str):
        url = urljoin(self.GITHUB_CLIENT_URL, url_segment)

        headers = {
            "Authorization": self.AUTH,
        }

        response = requests.get(url, headers=headers)

        return response

    def _post_request(self, url_segment: str, body: Dict[str, Any]):
        url = urljoin(self.GITHUB_CLIENT_URL, url_segment)

        headers = {
            "Authorization": self.AUTH,
        }

        response = requests.post(url, headers=headers, json=body)

        return response

    def _patch_request(self, url_segment: str, body: Dict[str, Any]):
        url = urljoin(self.GITHUB_CLIENT_URL, url_segment)

        headers = {
            "Authorization": self.AUTH,
        }

        response = requests.patch(url, headers=headers, json=body)

        return response

    def get_reference(self, owner: str, repo: str, ref: str):
        path = f"/repos/{owner}/{repo}/git/refs/{ref}" 

        return self._get_request(path)

    def get_commit(self, owner: str, repo: str, sha: str):
        path = f"/repos/{owner}/{repo}/git/commits/{sha}"

        return self._get_request(path)

    def create_commit(self, owner: str, repo: str, body: Dict[str, Any]):
        path = f"/repos/{owner}/{repo}/git/commits"

        return self._post_request(
            url_segment=path,
            body=body,
        )
    
    def update_reference(self, owner: str, repo: str, ref: str, body: Dict[str, Any]):
        path = f"/repos/{owner}/{repo}/git/refs/{ref}"

        return self._patch_request(
            url_segment=path,
            body=body,
        )

    def create_empty_commit(self):
        owner = "sumatokado"
        repo = "vapid-contributions"
        ref = "heads/master"

        resp = self.get_reference(owner, repo, ref)
        reference_commit_sha = resp.json()["object"]["sha"]

        resp = self.get_commit(owner, repo, reference_commit_sha)
        tree_sha = resp.json()["tree"]["sha"]

        body = {
            "tree": tree_sha,
            "parents": [reference_commit_sha],
            "message": "empty commit",
        }
        resp = self.create_commit(owner, repo, body)
        new_commit_sha = resp.json()["sha"]

        body = {
            "sha": new_commit_sha,
            "force": False,
        }
        resp = self.update_reference(owner, repo, ref, body)

client = GithubWriteClient()
client.create_empty_commit()