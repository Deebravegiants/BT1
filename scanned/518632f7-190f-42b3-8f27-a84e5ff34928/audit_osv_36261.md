# [M] prompts.chat SSRF via Fal.ai Media Status Polling

## Summary
Severity: Medium
Advisory: CVE-2026-22664
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-22664
Type: osv

## Details
prompts.chat prior to commit 30a8f04 contains a server-side request forgery vulnerability in the Fal.ai media status polling feature that allows authenticated users to perform arbitrary outbound requests by supplying attacker-controlled URLs in the token parameter. Attackers can exploit the lack of URL validation to disclose the FAL_API_KEY in the Authorization header, enabling credential theft, internal network probing, and abuse of the victim's Fal.ai account.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22664.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22664
- https://www.vulncheck.com/advisories/prompts-chat-ssrf-via-fal-ai-media-status-polling
- https://gist.github.com/mdisec/27c0cac0ec6a8f3c8f85a18987ddb942
- https://github.com/f/prompts.chat/commit/30a8f0470e0ba45e6be9c9f55220f4a9a6b91c99
- https://github.com/f/prompts.chat
