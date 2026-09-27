# [H] Wekan Vulnerable to SSRF through Lack of Validation or Filtering in Attachment URL Loading

## Summary
Severity: High
Advisory: CVE-2026-30844
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-30844
Type: osv

## Details
Wekan is an open source kanban tool built with Meteor. Versions 8.32 and 8.33 are vulnerable to Server-Side Request Forgery (SSRF) via attachment URL loading. During board import in Wekan, attachment URLs from user-supplied JSON data are fetched directly by the server without any URL validation or filtering, affecting both the Wekan and Trello import flows. The parseActivities() and parseActions() methods extract user-controlled attachment URLs, which are then passed directly to Attachments.load() for download with no sanitization. This Server-Side Request Forgery (SSRF) vulnerability allows any authenticated user to make the server issue arbitrary HTTP requests, potentially accessing internal network services such as cloud instance metadata endpoints (exposing IAM credentials), internal databases, and admin panels that are otherwise unreachable from outside the network. This issue has been fixed in version 8.34.

## References
- https://github.com/wekan/wekan/releases/tag/v8.34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30844.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30844
- https://securitylab.github.com/advisories/GHSL-2026-045_Wekan/
- https://github.com/wekan/wekan/commit/62216e36c15f55d4ef6cb97313db3aa54fc77fe0
