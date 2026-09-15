# [C] CVE-2023-28531

## Summary
Severity: Critical
Advisory: CVE-2023-28531
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-17
Source: https://osv.dev/vulnerability/CVE-2023-28531
Type: osv

## Details
ssh-add in OpenSSH before 9.3 adds smartcard keys to ssh-agent without the intended per-hop destination constraints. The earliest affected version is 8.9.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AN2UDTXEUSKFIOIYMV6JNI5VSBMYZOFT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AN2UDTXEUSKFIOIYMV6JNI5VSBMYZOFT/
- https://security.gentoo.org/glsa/202307-01
- https://security.netapp.com/advisory/ntap-20230413-0008/
- https://www.debian.org/security/2023/dsa-5586
- https://www.openwall.com/lists/oss-security/2023/03/15/8
