# [M] X.org Server xkb.c _GetCountedString buffer overflow

## Summary
Severity: Medium
Advisory: CVE-2022-3550
CVSS: 5.5 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3550
Type: osv

## Details
A vulnerability classified as critical was found in X.org Server. Affected by this vulnerability is the function _GetCountedString of the file xkb/xkb.c. The manipulation leads to buffer overflow. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-211051.

## References
- https://cgit.freedesktop.org/xorg/xserver/commit/?id=11beef0b7f1ed290348e45618e5fa0d2bffcb72e
- https://vuldb.com/?id.211051
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3550.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3QTPFVGYTOY4EWTJEBH3YGDTTU57FZAK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IOEDFBYPSE3EMVHTEFCVEJD2R2Y5F2A5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OXZZ6JBDBVBYPDI6DUTY6N36GNW37YHK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X7W3NXSYK4P3XCZQBI3U6UWP4DPZIMRZ/
- https://nvd.nist.gov/vuln/detail/CVE-2022-3550
- https://security.gentoo.org/glsa/202305-30
- https://www.debian.org/security/2022/dsa-5278
- https://lists.debian.org/debian-lts-announce/2022/11/msg00012.html
