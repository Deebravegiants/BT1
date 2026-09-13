# [H] CVE-2026-77642

## Summary
Severity: High
Advisory: CVE-2026-77642
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77642
Type: osv

## Details
tor before 0.4.9.9 was prone to an out-of-bounds write when parsing a consensus or  detached signature with unexpected signature digest type. Impact  is minor for most Tor roles, but potentially major for directory   authorities. This is TROVE-2026-019.

## References
- https://gitlab.torproject.org/tpo/core/tor/-/raw/tor-0.4.9.9/ChangeLog
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77642.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77642
