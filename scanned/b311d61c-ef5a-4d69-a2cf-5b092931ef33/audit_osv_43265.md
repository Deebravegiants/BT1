# [C] DB-GPT v0.8.1 Path Traversal Arbitrary File Write via user_id Header

## Summary
Severity: Critical
Advisory: CVE-2026-73034
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73034
Type: osv

## Details
DB-GPT v0.8.1 contains an unauthenticated path traversal vulnerability that allows remote attackers to write arbitrary files to any location on the server by injecting directory traversal sequences into the user_id HTTP header of the Python file-upload endpoint. Attackers can send a crafted multipart upload request with a traversal-poisoned user_id header to escape the intended upload directory and write attacker-controlled content to locations such as Python startup hooks, cron directories, or agent scripts, resulting in remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73034.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73034
- https://www.vulncheck.com/advisories/db-gpt-path-traversal-arbitrary-file-write-via-user-id-header
- https://github.com/eosphoros-ai/DB-GPT/issues/3104
- https://github.com/eosphoros-ai/DB-GPT/commit/e0c741bd2b5e521b128cffb3f68982dde3f7b359
- https://github.com/eosphoros-ai/DB-GPT
