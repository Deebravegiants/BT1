# [M] prompts.chat Authorization Bypass Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-22663
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-22663
Type: osv

## Details
prompts.chat prior to commit 7b81836 contains multiple authorization bypass vulnerabilities due to missing isPrivate checks across API endpoints and page metadata generation that allow unauthorized users to access sensitive data associated with private prompts. Attackers can exploit these missing authorization checks to retrieve private prompt version history, change requests, examples, current content, and metadata including titles and descriptions exposed via HTML meta tags.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22663.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22663
- https://www.vulncheck.com/advisories/prompts-chat-authorization-bypass-information-disclosure
- https://github.com/f/prompts.chat/pull/1104
- https://github.com/f/prompts.chat/commit/7b81836b214f2796aaf37ded2944eadc978afd35
- https://github.com/f/prompts.chat
