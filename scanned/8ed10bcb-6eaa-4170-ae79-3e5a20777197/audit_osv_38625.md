# [H] Caching of Authentication allows Authentication Bypass in qSnapper

## Summary
Severity: High
Advisory: CVE-2026-41048
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-41048
Type: osv

## Details
Incorrect caching of authentication between different polkit methods in qSnapper before version 1.3.3 allowed a local attacker to use functions like "restore from snapshot" even if only allowed to do "delete snapshot".

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41048.json
- https://github.com/presire/qSnapper/releases/tag/v1.3.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41048
- https://security.opensuse.org/2026/05/26/qsnapper-dbus-issues.html#issue-auth-caching
- https://bugzilla.suse.com/show_bug.cgi?id=1262218
- https://github.com/presire/qSnapper
