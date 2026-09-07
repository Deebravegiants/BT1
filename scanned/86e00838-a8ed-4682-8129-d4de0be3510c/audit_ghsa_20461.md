# [H] Cross-Site Request Forgery in yetiforce

## Summary
Severity: High
Advisory: GHSA-7g7r-gr46-q4p5
CVE: CVE-2022-0269
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-7g7r-gr46-q4p5
Type: github-advisory

## Affected
- Packagist: `yetiforce/yetiforce-crm` — affected >=0

## Details
Versions of yetiforce 6.3.0 and prior are subject to privilege escalation via a cross site request forgery bug. This allows an attacker to create a new admin account even with SameSite: Strict enabled. This vulnerability can be exploited by any user on the system including guest users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0269
- https://github.com/yetiforcecompany/yetiforcecrm/commit/298c7870e6fe4332d8aa1757a9c8d79f841389ff
- https://github.com/yetiforcecompany/yetiforcecrm
- https://huntr.dev/bounties/a0470915-f6df-45b8-b3a2-01aebe764df0
