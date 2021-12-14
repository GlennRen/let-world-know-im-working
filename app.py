from client import GithubReadClient
from client_write import GithubWriteClient

reader = GithubReadClient()
contributions = reader.calculate_contributions()
# writer = GithubWriteClient()
# writer.create_commits_for_contributions(contributions)
print(contributions)