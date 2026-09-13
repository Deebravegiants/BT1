# [M] NextChat 2.15.8 through 2.16.1 OpenAI API Key Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-82639
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-82639
Type: osv

## Details
NextChat versions from 2.15.8 through 2.16.1 contain an improper URL validation vulnerability in the proxy endpoint that allows attackers to obtain the server's OpenAI API key. The x-base-url header is validated using substring matching instead of hostname parsing, allowing any URL containing 'api.openai.com' to pass validation and receive the server's credentials in the Authorization header.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82639.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82639
- https://www.vulncheck.com/advisories/nextchat-2.15.8-through-2.16.1-openai-api-key-disclosure
- https://github.com/ChatGPTNextWeb/NextChat/issues/6814
- https://github.com/ChatGPTNextWeb/NextChat
- https://github.com/ChatGPTNextWeb/NextChat/blob/v2.16.1/app/api/proxy.ts
