# [M] CVE-2026-41525

## Summary
Severity: Medium
Advisory: CVE-2026-41525
CVSS: 6.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/CVE-2026-41525
Type: osv

## Details
KDE Dolphin before 25.12.3 allows applications in a Flatpak (or with AppArmor confinement) to open folders outside of the application sandbox without additional scrutiny. Dolphin's implementation of the FileManager1 protocol allows the path given to be any type of file, including scripts or executables. (By default, Dolphin will then prompt the user to determine if they want to launch a script or executable; however, the intended behavior is to block the attempted action, not present a consent prompt.)

## References
- http://www.openwall.com/lists/oss-security/2026/05/19/1
- https://github.com/KDE/dolphin/releases/tag/v25.12.3
- https://invent.kde.org/system/dolphin/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41525.json
- https://kde.org/info/security/advisory-20260427-2.txt
- https://nvd.nist.gov/vuln/detail/CVE-2026-41525
