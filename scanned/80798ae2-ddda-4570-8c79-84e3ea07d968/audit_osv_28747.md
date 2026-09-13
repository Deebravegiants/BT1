# [C] CVE-2024-36048

## Summary
Severity: Critical
Advisory: CVE-2024-36048
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-18
Source: https://osv.dev/vulnerability/CVE-2024-36048
Type: osv

## Details
QAbstractOAuth in Qt Network Authorization in Qt before 5.15.17, 6.x before 6.2.13, 6.3.x through 6.5.x before 6.5.6, and 6.6.x through 6.7.x before 6.7.1 uses only the time to seed the PRNG, which may result in guessable values.

## References
- https://codereview.qt-project.org/c/qt/qtnetworkauth/+/560317
- https://codereview.qt-project.org/c/qt/qtnetworkauth/+/560368
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RGB6KUPJFQWUBKXVDPJUMAD6KNJJEWPW/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZOOZZZSK5PNRHFGQMUGUHVYWLILFJCRS/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZPHAI3DKDCIU6XLNS6PV6GFS2PHH3GZM/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36048.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RGB6KUPJFQWUBKXVDPJUMAD6KNJJEWPW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZOOZZZSK5PNRHFGQMUGUHVYWLILFJCRS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZPHAI3DKDCIU6XLNS6PV6GFS2PHH3GZM/
- https://nvd.nist.gov/vuln/detail/CVE-2024-36048
