# [M] Information leak via “diff” methods in qSnapper

## Summary
Severity: Medium
Advisory: CVE-2026-41047
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-41047
Type: osv

## Details
Lack of authentication when using the "snapshot diff" functions in qSnapper before version 1.3.3 allowed a local attacker to see otherwise read protected information.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41047.json
- https://github.com/presire/qSnapper/releases/tag/v1.3.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41047
- https://security.opensuse.org/2026/05/26/qsnapper-dbus-issues.html#issue-info-leak
- https://bugzilla.suse.com/show_bug.cgi?id=1261890
- https://github.com/presire/qSnapper
