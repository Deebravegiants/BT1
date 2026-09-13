# [H] CVE-2023-3390

## Summary
Severity: High
Advisory: CVE-2023-3390
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-28
Source: https://osv.dev/vulnerability/CVE-2023-3390
Type: osv

## Details
A use-after-free vulnerability was found in the Linux kernel's netfilter subsystem in net/netfilter/nf_tables_api.c.

Mishandled error handling with NFT_MSG_NEWRULE makes it possible to use a dangling pointer in the same transaction causing a use-after-free vulnerability. This flaw allows a local attacker with user access to cause a privilege escalation issue.

We recommend upgrading past commit 1240eb93f0616b21c675416516ff3d74798fdc97.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://security.netapp.com/advisory/ntap-20230818-0004/
- https://www.debian.org/security/2023/dsa-5448
- https://www.debian.org/security/2023/dsa-5461
- http://packetstormsecurity.com/files/174577/Kernel-Live-Patch-Security-Notice-LSN-0097-1.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00001.html
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=1240eb93f0616b21c675416516ff3d74798fdc97
- https://kernel.dance/1240eb93f0616b21c675416516ff3d74798fdc97
