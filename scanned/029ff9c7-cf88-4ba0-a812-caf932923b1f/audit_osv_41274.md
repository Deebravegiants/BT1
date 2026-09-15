# [M] LobeChat < 2.2.10-canary.18 - SSRF via importFromUrl and fetchImageFromUrl

## Summary
Severity: Medium
Advisory: CVE-2026-59095
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-59095
Type: osv

## Details
LobeChat before 2.2.10-canary.18 contains a server-side request forgery vulnerability that allows authenticated attackers to direct internal HTTP requests to arbitrary URLs by supplying user-controlled input to the skill import service (importFromUrl) and topic cover update (fetchImageFromUrl) endpoints, which use the global fetch without the project's ssrf-safe-fetch wrapper. Attackers can target internal addresses such as cloud instance metadata endpoints through these unprotected code paths to disclose internal service responses and cloud credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59095.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59095
- https://www.vulncheck.com/advisories/lobechat-canary-18-ssrf-via-importfromurl-and-fetchimagefromurl
- https://github.com/lobehub/lobehub/pull/16601
- https://github.com/lobehub/lobehub
- https://github.com/lobehub/lobehub/issues/16536
