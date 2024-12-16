from mygithub import GithubService
from utils import throw_if_missing
import asyncio
import os


async def handle_request(res, req, log, error):
   """
   Handles an incoming GitHub webhook request.


   :param res: Response object
   :param req: Request object
   :param log: Logging function
   :param error: Error logging function
   """
   try:
       throw_if_missing(os.environ, ["GITHUB_WEBHOOK_SECRET", "GITHUB_TOKEN"])


       github = GithubService()


       if not await github.verify_webhook(req):
           error("Invalid signature")
           return res.json({"ok": False, "error": "Invalid signature"}, status_code=401)


       if not github.is_issue_opened_event(req):
           log("Received non-issue event - ignoring")
           return res.json({"ok": True})


       await github.post_comment(
           req.json["repository"],
           req.json["issue"],
           f"Thanks for the issue report @{req.json['issue']['user']['login']}! "
           f"We will look into it as soon as possible."
       )


       return res.json({"ok": True})
   except Exception as e:
       error(f"An unexpected error occurred: {e}")
       return res.json({"ok": False, "error": "Internal Server Error"}, status_code=500)


# Mock request and response objects for testing
class MockRequest:
   def __init__(self, body_json, headers):
       self.body_json = body_json
       self.headers = headers


   @property
   def json(self):
       return self.body_json




class MockResponse:
   def json(self, data, status_code=200):
       print(f"Response: {status_code}, Data: {data}")
       return data


req = MockRequest(
   body_json={
       "repository": {"full_name": "example/repo"},
       "issue": {
           "number": 1,
           "user": {"login": "testuser"}
       }
   },
   headers={"X-Hub-Signature-256": "example_signature"}
)
res = MockResponse()


log = print
error = print 


asyncio.run(handle_request(res, req, log, error))
