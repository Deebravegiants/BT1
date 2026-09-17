# [C] CVE-2020-13910

## Summary
Severity: Critical
Advisory: CVE-2020-13910
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-06-07
Source: https://osv.dev/vulnerability/CVE-2020-13910
Type: osv

## Details
Pengutronix Barebox through v2020.05.0 has an out-of-bounds read in nfs_read_reply in net/nfs.c because a field of an incoming network packet is directly used as a length field without any bounds check.

## References
- https://git.pengutronix.de/cgit/barebox/commit/net/nfs.c?h=next&id=c0f0cbd1759a6ca6cbda4001dff5764f6633c825
