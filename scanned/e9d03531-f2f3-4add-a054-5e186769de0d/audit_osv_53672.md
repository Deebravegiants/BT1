# [H] CVE-2023-1252

## Summary
Severity: High
Advisory: CVE-2023-1252
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-23
Source: https://osv.dev/vulnerability/CVE-2023-1252
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s Ext4 File System in how a user triggers several file operations simultaneously with the overlay FS usage. This flaw allows a local user to crash or potentially escalate their privileges on the system. Only if patch 9a2544037600 ("ovl: fix use after free in struct ovl_aio_req") not applied yet, the kernel could be affected.

## References
- https://lore.kernel.org/lkml/20211115165433.449951285%40linuxfoundation.org/
- https://security.netapp.com/advisory/ntap-20230505-0005/
