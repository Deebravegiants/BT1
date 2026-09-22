# [H] CVE-2026-10564

## Summary
Severity: High
Advisory: CVE-2026-10564
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-10564
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.9.6 contains a Server-Side Request Forgery (SSRF). The legacy RSSReaderComponent in rss.py and SearXNG component in searxng.py make unvalidated HTTP requests to user-controlled URLs, bypassing SSRF protections introduced in version 1.9.3. An authenticated attacker can exploit this to access internal resources including cloud metadata services (AWS/Azure/GCP IMDS), potentially exfiltrating IAM credentials and enumerating internal networks. The vulnerability can also be triggered through prompt injection in agentic workflows due to tool_mode=True exposure.

## References
- https://www.ibm.com/support/pages/node/7277995
