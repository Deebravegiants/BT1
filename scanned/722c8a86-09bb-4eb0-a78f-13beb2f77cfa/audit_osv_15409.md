# [C] CVE-2019-15937

## Summary
Severity: Critical
Advisory: CVE-2019-15937
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-05
Source: https://osv.dev/vulnerability/CVE-2019-15937
Type: osv

## Details
Pengutronix barebox through 2019.08.1 has a remote buffer overflow in nfs_readlink_reply in net/nfs.c because a length field is directly used for a memcpy.

## References
- https://git.pengutronix.de/cgit/barebox/commit/net/nfs.c?h=next&id=84986ca024462058574432b5483f4bf9136c538d
