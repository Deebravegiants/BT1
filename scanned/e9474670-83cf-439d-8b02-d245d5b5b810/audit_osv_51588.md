# [H] CVE-2021-3444

## Summary
Severity: High
Advisory: CVE-2021-3444
Aliases: A-183694099, PUB-A-183694099
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-23
Source: https://osv.dev/vulnerability/CVE-2021-3444
Type: osv

## Details
The bpf verifier in the Linux kernel did not properly handle mod32 destination register truncation when the source register was known to be 0. A local attacker with the ability to load bpf programs could use this gain out-of-bounds reads in kernel memory leading to information disclosure (kernel memory), and possibly out-of-bounds writes that could potentially lead to code execution. This issue was addressed in the upstream kernel in commit 9b00f1b78809 ("bpf: Fix truncation handling for mod32 dst reg wrt zero") and in Linux stable kernels 5.11.2, 5.10.19, and 5.4.101.

## References
- http://www.openwall.com/lists/oss-security/2021/03/23/2
- https://lists.debian.org/debian-lts-announce/2021/10/msg00010.html
- https://security.netapp.com/advisory/ntap-20210416-0006/
- https://www.openwall.com/lists/oss-security/2021/03/23/2
- http://packetstormsecurity.com/files/162117/Kernel-Live-Patch-Security-Notice-LSN-0075-1.html
- http://packetstormsecurity.com/files/164950/Kernel-Live-Patch-Security-Notice-LSN-0082-1.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9b00f1b78809
