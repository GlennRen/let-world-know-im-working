import base64
import os
from urllib.parse import urljoin
from dateutil import parser
from datetime import datetime, timedelta, timezone


from collections import Counter
from pprint import pprint
import requests


# UTILS
def created_in_last_day(extract_date):
    def fn(obj):
        parsed_date = parser.parse(extract_date(obj)) 
        return parsed_date > datetime.now(timezone.utc) - timedelta(days=1)
    return fn

# PR
def get_author_from_pr(pr):
    return pr['user']['login']
def get_pr_number(pr):
    return pr["number"]

# REVIEW
def get_contributor_from_review(review):
    return review['user']['login']

# COMMIT
def get_author_from_commit(commit):
    return commit['author']['login']



class GithubClient:
    GITHUB_CLIENT_URL = "https://api.github.com"
    PAGE_SIZE = 100
    REPO_LIST = [
        "ramp/web",
        "ramp/core",
        "ramp/risk",
        "ramp/authorizer",
        "ramp/infra",
    ]
    

    def __init__(self):
        username = "john_ramp"
        access_token = os.environ["GITHUB_ACCESS_TOKEN"]

        auth = f"{username}:{access_token}"
        auth_bytes = auth.encode("ascii")
        auth_base64 = base64.b64encode(auth_bytes).decode("ascii")
        self.repo_name = 'ramp/infra'
        self.contributions = []

        self.AUTH = f"Basic {auth_base64}"

    
    def reset_contributions(self):
        self.contributions = []
    
    def set_repo(self, repo_name):
        if repo_name not in self.REPO_LIST:
            raise Exception('Please use a valid repo path')
            
        self.repo_name = repo_name
    
    def _get_request(self, url_segment: str, page_number):
        url = urljoin(self.GITHUB_CLIENT_URL, url_segment)

        headers = {
            "Authorization": self.AUTH,
        }

        params = {
            "per_page": self.PAGE_SIZE,
            "page": page_number
        }
        

        response = requests.get(url, headers=headers, params=params)

        return response
    
    def get_repo_commits(self):
        commits = self._get_request(
            url_segment=f"/repos/{self.repo_name}/commits", page_number=1
        ).json()
        get_date_from_commit = lambda x: x['commit']['author']['date']
        extract_fn = created_in_last_day(get_date_from_commit)
        return list(filter(extract_fn, commits))
    
    def _get_repo_filtered_pr_page(self, page_number):
        get_date_from_pr = lambda x: x['created_at']
        return list(filter(created_in_last_day(get_date_from_pr), self._get_request(
            url_segment=f"/repos/{self.repo_name}/pulls", page_number=page_number
        ).json()))
    
    def get_repo_prs(self):
        page_number = 1
        filtered_res = self._get_repo_filtered_pr_page(page_number)
        ret = filtered_res
        
        while (len(filtered_res) == self.PAGE_SIZE):
            page_number += 1
            filtered_res = self._get_repo_filtered_pr_page(page_number)
            ret.extend(filtered_res)
           
        return ret


    def get_pr_reviews(self, pr_number):
        return self._get_request(
            url_segment=f"/repos/ramp/core/pulls/{pr_number}/reviews", page_number=1
        ).json()


    def _append_commit_data(self):
        print('Extracting commit data...')
        for commit in self.get_repo_commits():
            try:
                self.contributions.append(get_author_from_commit(commit))
            except Exception as e:
                # Pre-commit has no author
                pass

    def _extract_contributors_from_pr(self, pr):
        pr_number = get_pr_number(pr)
        print (f'Extracting pr {pr_number}...')

        reviews = self.get_pr_reviews(pr_number)
        return [get_contributor_from_review(review) for review in reviews]

    def _append_pr_data(self):
        for pr in self.get_repo_prs():
            self.contributions.extend(self._extract_contributors_from_pr(pr))
            self.contributions.append(get_author_from_pr(pr))

        
    def calculate_contributions(self):
        for repo in self.REPO_LIST:
            print(f'Processing repo: {repo}')
            self.set_repo(repo)
            self._append_commit_data()
            self._append_pr_data()
        return Counter(self.contributions)
    