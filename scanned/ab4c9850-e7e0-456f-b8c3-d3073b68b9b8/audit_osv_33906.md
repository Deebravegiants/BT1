# [H] Mail-0 Zero Session Hijacking Via Email

## Summary
Severity: High
Advisory: CVE-2025-52557
Aliases: GHSA-34gh-g567-hq85
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-06-21
Source: https://osv.dev/vulnerability/CVE-2025-52557
Type: osv

## Details
Mail-0's Zero is an open-source email solution. In version 0.8 it's possible for an attacker to craft an email that executes javascript leading to session hijacking due to improper sanitization. This issue has been patched in version 0.81.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52557.json
- https://github.com/Mail-0/Zero/security/advisories/GHSA-34gh-g567-hq85
- https://nvd.nist.gov/vuln/detail/CVE-2025-52557
- https://github.com/Mail-0/Zero/commit/48d1df65b62c9c57897b72b241081f447140342f
- https://github.com/Mail-0/Zero/pull/1386
