# [C] JLSEC-2026-67

## Summary
Severity: Critical
Advisory: JLSEC-2026-67
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/JLSEC-2026-67
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=8.9.0+0 <9.3.2+0

## Details
ssh-add in OpenSSH before 9.3 adds smartcard keys to ssh-agent without the intended per-hop destination constraints. The earliest affected version is 8.9.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AN2UDTXEUSKFIOIYMV6JNI5VSBMYZOFT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AN2UDTXEUSKFIOIYMV6JNI5VSBMYZOFT/
- https://security.gentoo.org/glsa/202307-01
- https://security.netapp.com/advisory/ntap-20230413-0008/
- https://www.debian.org/security/2023/dsa-5586
- https://www.openwall.com/lists/oss-security/2023/03/15/8
