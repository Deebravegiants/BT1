# [M] GNOME project libxml2 v2.9.10 has a global buffer over-read vulnerability in...

## Summary
Severity: Medium
Advisory: JLSEC-2025-69
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-69
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=2.9.10+0 <2.9.12+0

## Details
GNOME project libxml2 v2.9.10 has a global buffer over-read vulnerability in xmlEncodeEntitiesInternal at `libxml2/entities.c`. The issue has been fixed in commit 50f06b3e.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00061.html
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/50f06b3efb638efb0abd95dc62dca05ae67882c2
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/178
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/09/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2NQ5GTDYOVH26PBCPYXXMGW5ZZXWMGZC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5KTUAGDLEHTH6HU66HBFAFTSQ3OKRAN3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/674LQPJO2P2XTBTREFR5LOZMBTZ4PZAY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7KQXOHIE3MNY3VQXEN7LDQUJNIHOVHAW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ENEHQIBMSI6TZVS35Y6I4FCTYUQDLJVP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H3IQ7OQXBKWD3YP7HO6KCNOMLE5ZO2IR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J3ICASXZI2UQYFJAOQWHSTNWGED3VXOE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JCHXIWR5DHYO3RSO7RAHEC6VJKXD2EH2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O7MEWYKIKMV2SKMGH4IDWVU3ZGJXBCPQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RIQAMBA2IJUTQG5VOP5LZVIZRNCKXHEQ/
- https://security.gentoo.org/glsa/202107-05
- https://security.netapp.com/advisory/ntap-20200924-0001/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
