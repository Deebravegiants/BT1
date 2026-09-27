# [H] CVE-2021-38201

## Summary
Severity: High
Advisory: CVE-2021-38201
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-08
Source: https://osv.dev/vulnerability/CVE-2021-38201
Type: osv

## Details
net/sunrpc/xdr.c in the Linux kernel before 5.13.4 allows remote attackers to cause a denial of service (xdr_set_page_base slab-out-of-bounds access) by performing many NFS 4.2 READ_PLUS operations.

## References
- https://security.netapp.com/advisory/ntap-20210902-0010/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.4
- https://github.com/torvalds/linux/commit/6d1c0f3d28f98ea2736128ed3e46821496dc3a8c
