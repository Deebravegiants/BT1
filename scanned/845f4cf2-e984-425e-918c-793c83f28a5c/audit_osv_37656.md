# [H] AnythingLLM Permissable CORS policy

## Summary
Severity: High
Advisory: CVE-2026-32617
Aliases: GHSA-24qj-pw4h-3jmm
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32617
Type: osv

## Details
AnythingLLM is an application that turns pieces of content into context that any LLM can use as references during chatting. In 1.11.1 and earlier, On default installations where no password or API key has been configured, all HTTP endpoints and the agent WebSocket lack authentication, and the server's CORS policy accepts any origin. AnythingLLM Desktop binds to 127.0.0.1 (loopback) by default. Modern browsers (Chrome, Edge, Firefox) implement Private Network Access (PNA). This explicitly blocks public websites from making requests to local IP addresses. Exploitation is only viable from within the same local network (LAN) due to browser-level blocking of public-to-private requests.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32617.json
- https://github.com/Mintplex-Labs/anything-llm/security/advisories/GHSA-24qj-pw4h-3jmm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32617
