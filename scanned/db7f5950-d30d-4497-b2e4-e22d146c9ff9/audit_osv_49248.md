# [M] CVE-2018-7492

## Summary
Severity: Medium
Advisory: CVE-2018-7492
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-26
Source: https://osv.dev/vulnerability/CVE-2018-7492
Type: osv

## Details
A NULL pointer dereference was found in the net/rds/rdma.c __rds_rdma_map() function in the Linux kernel before 4.14.7 allowing local attackers to cause a system panic and a denial-of-service, related to RDS_GET_MR and RDS_GET_MR_FOR_DEST.

## References
- https://usn.ubuntu.com/3674-1/
- https://usn.ubuntu.com/3677-1/
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3674-2/
- https://usn.ubuntu.com/3677-2/
- http://www.securityfocus.com/bid/103185
- https://usn.ubuntu.com/3619-2/
- https://www.debian.org/security/2018/dsa-4187
- https://bugzilla.redhat.com/show_bug.cgi?id=1527393
- https://patchwork.kernel.org/patch/10096441/
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.7
- https://xorl.wordpress.com/2017/12/18/linux-kernel-rdma-null-pointer-dereference/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f3069c6d33f6ae63a1668737bc78aaaa51bff7ca
- https://github.com/torvalds/linux/commit/f3069c6d33f6ae63a1668737bc78aaaa51bff7ca
