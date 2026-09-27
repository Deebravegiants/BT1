# [H] CVE-2021-29154

## Summary
Severity: High
Advisory: CVE-2021-29154
Aliases: A-185462528, PUB-A-185462528
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-08
Source: https://osv.dev/vulnerability/CVE-2021-29154
Type: osv

## Details
BPF JIT compilers in the Linux kernel through 5.11.12 have incorrect computation of branch displacements, allowing them to execute arbitrary code within the kernel context. This affects arch/x86/net/bpf_jit_comp.c and arch/x86/net/bpf_jit_comp32.c.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=e4d4d456436bfb2fe412ee2cd489f7658449b098
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=26f55a59dc65ff77cd1c4b37991e26497fc68049
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W5YFGIIF24475A2LNW3UWHW2SNCS3G7M/
- http://packetstormsecurity.com/files/162434/Kernel-Live-Patch-Security-Notice-LSN-0076-1.html
- https://security.netapp.com/advisory/ntap-20210604-0006/
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://news.ycombinator.com/item?id=26757760
- https://www.openwall.com/lists/oss-security/2021/04/08/1
