# [H] CVE-2023-35788

## Summary
Severity: High
Advisory: CVE-2023-35788
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/CVE-2023-35788
Type: osv

## Details
An issue was discovered in fl_set_geneve_opt in net/sched/cls_flower.c in the Linux kernel before 6.3.7. It allows an out-of-bounds write in the flower classifier code via TCA_FLOWER_KEY_ENC_OPTS_GENEVE packets. This may result in denial of service or privilege escalation.

## References
- http://packetstormsecurity.com/files/174577/Kernel-Live-Patch-Security-Notice-LSN-0097-1.html
- https://www.debian.org/security/2023/dsa-5480
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://security.netapp.com/advisory/ntap-20230714-0002/
- https://www.debian.org/security/2023/dsa-5448
- https://git.kernel.org/linus/4d56304e5827c8cc8cc18c75343d283af7c4825c
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.7
- http://www.openwall.com/lists/oss-security/2023/06/17/1
- https://www.openwall.com/lists/oss-security/2023/06/07/1
