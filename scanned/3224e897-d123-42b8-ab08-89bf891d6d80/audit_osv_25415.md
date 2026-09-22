# [H] Use-after-free in Linux kernel's net/sched: cls_u32 component

## Summary
Severity: High
Advisory: CVE-2023-3609
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-21
Source: https://osv.dev/vulnerability/CVE-2023-3609
Type: osv

## Details
A use-after-free vulnerability in the Linux kernel's net/sched: cls_u32 component can be exploited to achieve local privilege escalation.

If tcf_change_indev() fails, u32_set_parms() will immediately return an error after incrementing or decrementing the reference counter in tcf_bind_filter(). If an attacker can control the reference counter and set it to zero, they can cause the reference to be freed, leading to a use-after-free vulnerability.

We recommend upgrading past commit 04c55383fa5689357bcdd2c8036725a55ed632bc.

## References
- http://packetstormsecurity.com/files/175072/Kernel-Live-Patch-Security-Notice-LSN-0098-1.html
- http://packetstormsecurity.com/files/175963/Kernel-Live-Patch-Security-Notice-LSN-0099-1.html
- https://git.kernel.org
- https://kernel.dance/04c55383fa5689357bcdd2c8036725a55ed632bc
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3609.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3609
- https://security.netapp.com/advisory/ntap-20230818-0005/
- https://www.debian.org/security/2023/dsa-5480
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit?id=04c55383fa5689357bcdd2c8036725a55ed632bc
