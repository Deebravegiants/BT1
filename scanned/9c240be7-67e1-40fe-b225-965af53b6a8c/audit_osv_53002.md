# [H] CVE-2022-25636

## Summary
Severity: High
Advisory: CVE-2022-25636
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/CVE-2022-25636
Type: osv

## Details
net/netfilter/nf_dup_netdev.c in the Linux kernel 5.4 through 5.6.10 allows local users to gain privileges because of a heap out-of-bounds write. This is related to nf_tables_offload.

## References
- https://security.netapp.com/advisory/ntap-20220325-0002/
- https://www.debian.org/security/2022/dsa-5095
- http://packetstormsecurity.com/files/166444/Kernel-Live-Patch-Security-Notice-LSN-0085-1.html
- http://www.openwall.com/lists/oss-security/2022/02/22/1
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://git.kernel.org/pub/scm/linux/kernel/git/netfilter/nf.git/commit/?id=b1a5983f56e371046dcf164f90bfaf704d2b89f6
- https://www.openwall.com/lists/oss-security/2022/02/21/2
- https://github.com/Bonfee/CVE-2022-25636
- https://nickgregory.me/linux/security/2022/03/12/cve-2022-25636/
