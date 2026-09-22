# [H] Host header poisoning allows account takeover via password reset email

## Summary
Severity: High
Advisory: CVE-2024-32642
Aliases: GHSA-qjm6-c8hx-ffh8
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/CVE-2024-32642
Type: osv

## Details
Masa CMS is an open source Enterprise Content Management platform. Prior to 7.2.8, 7.3.13, and 7.4.6, there is vulnerable to host header poisoning which allows account takeover via password reset email. This vulnerability is fixed in 7.2.8, 7.3.13, and 7.4.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32642.json
- https://github.com/MasaCMS/MasaCMS/security/advisories/GHSA-qjm6-c8hx-ffh8
- https://nvd.nist.gov/vuln/detail/CVE-2024-32642
- https://github.com/MasaCMS/MasaCMS/commit/7541b9c99fb9e32d1de6f2658750525cec1d8960
