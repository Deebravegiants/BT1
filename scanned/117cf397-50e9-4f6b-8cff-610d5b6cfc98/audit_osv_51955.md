# [M] CVE-2021-46283

## Summary
Severity: Medium
Advisory: CVE-2021-46283
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-11
Source: https://osv.dev/vulnerability/CVE-2021-46283
Type: osv

## Details
nf_tables_newset in net/netfilter/nf_tables_api.c in the Linux kernel before 5.12.13 allows local users to cause a denial of service (NULL pointer dereference and general protection fault) because of the missing initialization for nft_set_elem_expr_alloc. A local user can set a netfilter table expression in their own namespace.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.13
- https://syzkaller.appspot.com/bug?id=22c3987f75a7b90e238a26b5a5920525c2d1f345
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ad9f151e560b016b6ad3280b48e42fa11e1a5440
