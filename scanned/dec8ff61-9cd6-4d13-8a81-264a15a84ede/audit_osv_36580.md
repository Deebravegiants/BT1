# [H] AnythingLLM vulnerable to Path Traversal

## Summary
Severity: High
Advisory: CVE-2026-24478
Aliases: GHSA-jp2f-99h9-7vjv
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2026-24478
Type: osv

## Details
AnythingLLM is an application that turns pieces of content into context that any LLM can use as references during chatting. Prior to version 1.10.0, a critical Path Traversal vulnerability in the DrupalWiki integration allows a malicious admin (or an attacker who can convince an admin to configure a malicious DrupalWiki URL) to write arbitrary files to the server. This can lead to Remote Code Execution (RCE) by overwriting configuration files or writing executable scripts. Version 1.10.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24478.json
- https://github.com/Mintplex-Labs/anything-llm/security/advisories/GHSA-jp2f-99h9-7vjv
- https://nvd.nist.gov/vuln/detail/CVE-2026-24478
