# [M] WWBN AVideo Authentication Bypass via X-Real-IP Header

## Summary
Severity: Medium
Advisory: CVE-2026-84476
Aliases: GHSA-gg65-574p-h4wc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84476
Type: osv

## Details
WWBN AVideo fails to validate trusted proxies before accepting X-Real-IP and X-Forwarded-For headers, allowing attackers to spoof the client address used by enforceRateLimit(). Attackers can rotate the header value per request to bypass login rate limiting and perform unlimited credential guessing attacks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84476.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-gg65-574p-h4wc
- https://nvd.nist.gov/vuln/detail/CVE-2026-84476
- https://www.vulncheck.com/advisories/wwbn-avideo-authentication-bypass-via-x-real-ip-header
