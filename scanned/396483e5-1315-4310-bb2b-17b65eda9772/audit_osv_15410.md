# [C] CVE-2019-15938

## Summary
Severity: Critical
Advisory: CVE-2019-15938
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-05
Source: https://osv.dev/vulnerability/CVE-2019-15938
Type: osv

## Details
Pengutronix barebox through 2019.08.1 has a remote buffer overflow in nfs_readlink_req in fs/nfs.c because a length field is directly used for a memcpy.

## References
- https://git.pengutronix.de/cgit/barebox/commit/fs/nfs.c?h=next&id=574ce994016107ad8ab0f845a785f28d7eaa5208
