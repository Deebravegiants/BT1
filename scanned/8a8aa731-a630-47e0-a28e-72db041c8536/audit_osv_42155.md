# [M] FileCodeBox < 2.4 Anti-bruteforce Rate Limit Bypass via Spoofed Headers

## Summary
Severity: Medium
Advisory: CVE-2026-64619
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-64619
Type: osv

## Details
FileCodeBox before 2.4 contains a rate-limit bypass vulnerability in the IPRateLimit class that allows unauthenticated attackers to circumvent request throttling by supplying attacker-controlled X-Real-IP and X-Forwarded-For headers without verification of trusted reverse proxy origin. Attackers can supply unique spoofed IP values on each request to enumerate all possible share codes and retrieve other users' files without authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64619.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64619
- https://www.vulncheck.com/advisories/filecodebox-anti-bruteforce-rate-limit-bypass-via-spoofed-headers
- https://github.com/vastsa/FileCodeBox/issues/479
- https://github.com/vastsa/FileCodeBox/commit/1b6d8e7277d3cfa34dc7a85803731d927b2147da
- https://github.com/vastsa/FileCodeBox/releases/tag/V2.4
- https://github.com/vastsa/FileCodeBox
