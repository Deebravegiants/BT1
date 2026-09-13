# [H] CVE-2019-20797

## Summary
Severity: High
Advisory: CVE-2019-20797
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-18
Source: https://osv.dev/vulnerability/CVE-2019-20797
Type: osv

## Details
An issue was discovered in e6y prboom-plus 2.5.1.5. There is a buffer overflow in client and server code responsible for handling received UDP packets, as demonstrated by I_SendPacket or I_SendPacketTo in i_network.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00028.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/77J22ZEQXS5SAYZGBDJ475AKFFJNKX5L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P3WS7GRZUIHCGLFET33MGC3PEKCH37W6/
- https://sourceforge.net/p/prboom-plus/bugs/252/
- https://sourceforge.net/p/prboom-plus/bugs/253/
- https://logicaltrust.net/blog/2019/10/prboom1.html
