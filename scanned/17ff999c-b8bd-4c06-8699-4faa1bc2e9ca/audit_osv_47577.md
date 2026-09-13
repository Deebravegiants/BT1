# [H] CVE-2016-8636

## Summary
Severity: High
Advisory: CVE-2016-8636
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-22
Source: https://osv.dev/vulnerability/CVE-2016-8636
Type: osv

## Details
Integer overflow in the mem_check_range function in drivers/infiniband/sw/rxe/rxe_mr.c in the Linux kernel before 4.9.10 allows local users to cause a denial of service (memory corruption), obtain sensitive information from kernel memory, or possibly have unspecified other impact via a write or read request involving the "RDMA protocol over infiniband" (aka Soft RoCE) technology.

## References
- http://www.securityfocus.com/bid/96189
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.10
- https://bugzilla.redhat.com/show_bug.cgi?id=1421981
- https://eyalitkin.wordpress.com/2017/02/11/cve-publication-cve-2016-8636/
- https://github.com/torvalds/linux/commit/647bf3d8a8e5777319da92af672289b2a6c4dc66
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=647bf3d8a8e5777319da92af672289b2a6c4dc66
- http://www.openwall.com/lists/oss-security/2017/02/11/9
