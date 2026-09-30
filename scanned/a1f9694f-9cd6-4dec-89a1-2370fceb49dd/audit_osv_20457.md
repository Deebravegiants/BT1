# [H] CVE-2021-33909

## Summary
Severity: High
Advisory: CVE-2021-33909
Aliases: A-195082750, ASB-A-195082750
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/CVE-2021-33909
Type: osv

## Details
fs/seq_file.c in the Linux kernel 3.16 through 5.13.x before 5.13.4 does not properly restrict seq buffer allocations, leading to an integer overflow, an Out-of-bounds Write, and escalation to root by an unprivileged user, aka CID-8cae8cd89f05.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z4UHHIGISO3FVRF4CQNJS4IKA25ATSFU/
- http://packetstormsecurity.com/files/165477/Kernel-Live-Patch-Security-Notice-LSN-0083-1.html
- http://www.openwall.com/lists/oss-security/2021/09/17/4
- https://lists.debian.org/debian-lts-announce/2021/07/msg00015.html
- http://www.openwall.com/lists/oss-security/2021/07/22/7
- https://lists.debian.org/debian-lts-announce/2021/07/msg00014.html
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2022-0015
- https://www.debian.org/security/2021/dsa-4941
- http://packetstormsecurity.com/files/163671/Kernel-Live-Patch-Security-Notice-LSN-0079-1.html
- http://packetstormsecurity.com/files/164155/Kernel-Live-Patch-Security-Notice-LSN-0081-1.html
- http://www.openwall.com/lists/oss-security/2021/08/25/10
- http://www.openwall.com/lists/oss-security/2021/09/17/2
- http://www.openwall.com/lists/oss-security/2021/09/21/1
- https://lists.debian.org/debian-lts-announce/2021/07/msg00016.html
- https://security.netapp.com/advisory/ntap-20210819-0004/
- https://github.com/torvalds/linux/commit/8cae8cd89f05f6de223d63e6d15e31c8ba9cf53b
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.4
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.openwall.com/lists/oss-security/2021/07/20/1
- http://packetstormsecurity.com/files/163621/Sequoia-A-Deep-Root-In-Linuxs-Filesystem-Layer.html
