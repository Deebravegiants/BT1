# [H] Weak polkit authentication check in qSnapper

## Summary
Severity: High
Advisory: CVE-2026-41045
CVSS: 8.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-41045
Type: osv

## Details
A time-to-check-time-of-use in polkit authentication of qSnapper before version 1.3.3 allowed a local attacker to bypass qSnappers authentication mechanism and operate e.g. as root user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41045.json
- https://github.com/presire/qSnapper/releases/tag/v1.3.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41045
- https://security.opensuse.org/2026/05/26/qsnapper-dbus-issues.html#issue-polkit-bypass
- https://bugzilla.suse.com/show_bug.cgi?id=1261795
- https://github.com/presire/qSnapper
