# [M] Velociraptor server crash via the SetPassword API

## Summary
Severity: Medium
Advisory: CVE-2026-18638
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-18638
Type: osv

## Details
Any authenticated Velociraptor user — including one holding only the readerrole — can terminate the entire server process with a single request, by calling SetPassword with a username that does not exist.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-18638/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18638.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18638
