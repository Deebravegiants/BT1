# [H] CVE-2021-38166

## Summary
Severity: High
Advisory: CVE-2021-38166
Aliases: A-197155069, PUB-A-197155069
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-07
Source: https://osv.dev/vulnerability/CVE-2021-38166
Type: osv

## Details
In kernel/bpf/hashtab.c in the Linux kernel through 5.13.8, there is an integer overflow and out-of-bounds write when many elements are placed in a single bucket. NOTE: exploitation might be impractical without the CAP_SYS_ADMIN capability.

## References
- https://lore.kernel.org/bpf/20210806150419.109658-1-th.yasumatsu%40gmail.com/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GUVLBJKZMWA3E3YXSH4SZ7BOYGJP4GXP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UL6CH5M5PRLMA3KPBX4LPUO6Z73GRISO/
- https://security.netapp.com/advisory/ntap-20210909-0001/
- https://www.debian.org/security/2021/dsa-4978
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf.git/commit/?id=c4eb1f403243fc7bbb7de644db8587c03de36da6
