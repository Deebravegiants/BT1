# [M] Adminer < 5.4.3 Cookie Injection via X-Forwarded-Prefix Header

## Summary
Severity: Medium
Advisory: CVE-2026-63771
Aliases: GHSA-c533-9qwm-8w5h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-63771
Type: osv

## Details
Adminer before 5.4.3 contains a cookie injection vulnerability that allows attackers to manipulate cookie attributes by injecting arbitrary values through the unsanitized X-Forwarded-Prefix HTTP header used in Set-Cookie path attributes. Attackers can exploit a misconfigured reverse proxy to downgrade SameSite protection and enable cross-origin authenticated requests, bypassing cookie security controls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63771.json
- https://github.com/vrana/adminer/releases#release-v5.4.3
- https://github.com/vrana/adminer/security/advisories/GHSA-c533-9qwm-8w5h
- https://nvd.nist.gov/vuln/detail/CVE-2026-63771
- https://www.vulncheck.com/advisories/adminer-cookie-injection-via-x-forwarded-prefix-header
- https://github.com/vrana/adminer/issues/1298
- https://github.com/vrana/adminer
