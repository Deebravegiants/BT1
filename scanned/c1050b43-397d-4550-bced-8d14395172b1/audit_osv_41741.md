# [M] Glance 0.8.5 IP Spoofing Authentication Brute-Force Protection Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-63770
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-63770
Type: osv

## Details
Glance through 0.8.5 contains an IP address spoofing vulnerability in the authentication handler that allows unauthenticated attackers to bypass brute-force lockout protections by supplying arbitrary values in the X-Forwarded-For request header when the server proxied option is enabled. Attackers can manipulate the leftmost value of the X-Forwarded-For header to make each login attempt appear to originate from a distinct IP address, preventing the per-IP failed-login counter from reaching the lockout threshold and enabling unlimited credential guessing against the authentication endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63770.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63770
- https://www.vulncheck.com/advisories/glance-ip-spoofing-authentication-brute-force-protection-bypass
- https://github.com/glanceapp/glance/issues/1031
- https://github.com/glanceapp/glance/commit/3f20e8d9d0b1983892632649f35fd00c7b4ea8b6
- https://github.com/glanceapp/glance/pull/1033
- https://github.com/glanceapp/glance
