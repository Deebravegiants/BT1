# [M] BIT-libpython-2021-3426

## Summary
Severity: Medium
Advisory: BIT-libpython-2021-3426
Aliases: BIT-python-2021-3426, BIT-python-min-2021-3426, CVE-2021-3426, PSF-2021-4
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2021-3426
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.3

## Details
There's a flaw in Python 3's pydoc. A local or adjacent attacker who discovers or is able to convince another local or adjacent user to start a pydoc server could access the server and use it to disclose sensitive information belonging to the other user that they would not normally be able to access. The highest risk of this flaw is to data confidentiality. This flaw affects Python versions before 3.8.9, Python versions before 3.9.3 and Python versions before 3.10.0.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1935913
- https://lists.debian.org/debian-lts-announce/2021/04/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00039.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/25HVHLBGO2KNPXJ3G426QEYSSCECJDU5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BF2K7HEWADHN6P52R3QLIOX27U3DJ4HI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DQYPUKLLBOZMKFPO7RD7CENTXHUUEUV7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LM5V4VPLBHBEASSAROYPSHXGXGGPHNOE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N6VXJZSZ6N64AILJX4CTMACYGQGHHD5C/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QNGAFMPIYIVJ47FCF2NK2PIX22HUG35B/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VPX7Y5GQDNB4FJTREWONGC4ZSVH7TGHF/
- https://nvd.nist.gov/vuln/detail/CVE-2021-3426
- https://security.gentoo.org/glsa/202104-04
- https://security.netapp.com/advisory/ntap-20210629-0003/
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
