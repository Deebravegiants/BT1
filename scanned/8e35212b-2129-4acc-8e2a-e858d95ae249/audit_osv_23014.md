# [M] CVE-2022-42012

## Summary
Severity: Medium
Advisory: CVE-2022-42012
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-09
Source: https://osv.dev/vulnerability/CVE-2022-42012
Type: osv

## Details
An issue was discovered in D-Bus before 1.12.24, 1.13.x and 1.14.x before 1.14.4, and 1.15.x before 1.15.2. An authenticated attacker can cause dbus-daemon and other programs that use libdbus to crash by sending a message with attached file descriptors in an unexpected format.

## References
- https://www.openwall.com/lists/oss-security/2022/10/06/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/42xxx/CVE-2022-42012.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E4CO7N226I3X5FNBR2MACCH6TS764VJP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ND74SKN56BCYL3QLEAAB6E64UUBRA5UG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SQCSLMCK2XGX23R2DKW2MSAICQAK6MT2/
- https://nvd.nist.gov/vuln/detail/CVE-2022-42012
- https://security.gentoo.org/glsa/202305-08
- https://gitlab.freedesktop.org/dbus/dbus/-/issues/417
