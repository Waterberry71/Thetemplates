import os
from octokit import Octokit
from octokit.webhook import verify
from dotenv import load_dotenv
import os


load_dotenv()


class GithubService:
   def init(self):
       # Initialize the Octokit client with authentication
       self.octokit = Octokit(auth="token", token=os.getenv("GITHUB_TOKEN"))


   async def verify_webhook(self, req):
       """
       Verifies the GitHub webhook signature.


       :param req: The HTTP request containing the webhook payload and headers
       :return: True if the webhook signature is valid, False otherwise
       """
       signature = req.headers.get("X-Hub-Signature-256")


       if not isinstance(signature, str):
           return False


       secret = os.getenv("GITHUB_WEBHOOK_SECRET")
       return await verify(req.headers, req.body, secret, events=["push"])


   def is_issue_opened_event(self, req):
       """
       Checks if the request is for an 'issues' event with an 'opened' action.


       :param req: The HTTP request
       :return: True if the event is an 'issues' opened event, False otherwise
       """
       return (
           req.headers.get("X-GitHub-Event") == "issues" and
           req.json.get("issue") and
           req.json.get("action") == "opened"
       )


   async def post_comment(self, repository, issue, comment):
       """
       Posts a comment on a GitHub issue.


       :param repository: The repository object
       :param issue: The issue object
       :param comment: The comment to post
       """
       await self.octokit.issues.create_comment(
           owner=repository["owner"]["login"],
           repo=repository["name"],
           issue_number=issue["number"],
           body=comment
       )
