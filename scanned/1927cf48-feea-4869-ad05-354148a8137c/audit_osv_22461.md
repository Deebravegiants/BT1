# [H] CVE-2022-29968

## Summary
Severity: High
Advisory: CVE-2022-29968
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-02
Source: https://osv.dev/vulnerability/CVE-2022-29968
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.17.5. io_rw_init_file in fs/io_uring.c lacks initialization of kiocb->private.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LU7MT7BPTA2NG24BTLZF5ZWYTLSO7BU3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TLWTG3TWIMLNQEVTA3ZQYVLLU2AJM3DY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XA7UZ3HS73KXVYCIKN5ZDH7LLLGPUMOZ/
- https://security.netapp.com/advisory/ntap-20220715-0009/
- https://github.com/torvalds/linux/commit/32452a3eb8b64e01e2be717f518c0be046975b9d
