# [M] CVE-2026-41527

## Summary
Severity: Medium
Advisory: CVE-2026-41527
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-41527
Type: osv

## Details
KDE Kleopatra before 26.08.0 on Windows allows local users to obtain the privileges of a Kleopatra user, because there is an error in the mechanism (KUniqueService) for ensuring that only one instance is running.

## References
- https://commits.kde.org/kleopatra/73471abb92d99c56354adb582bfaec2764c22b79
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41527.json
- https://kde.org/info/security/advisory-20260408-1.txt
- https://nvd.nist.gov/vuln/detail/CVE-2026-41527
- https://github.com/KDE/kleopatra/releases
