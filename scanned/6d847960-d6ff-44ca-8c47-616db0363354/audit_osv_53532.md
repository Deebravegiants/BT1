# [H] CVE-2022-47520

## Summary
Severity: High
Advisory: CVE-2022-47520
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-12-18
Source: https://osv.dev/vulnerability/CVE-2022-47520
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.0.11. Missing offset validation in drivers/net/wireless/microchip/wilc1000/hif.c in the WILC1000 wireless driver can trigger an out-of-bounds read when parsing a Robust Security Network (RSN) information element from a Netlink packet.

## References
- https://lore.kernel.org/r/20221123153543.8568-2-philipturnbull%40github.com
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://security.netapp.com/advisory/ntap-20230113-0007/
- https://github.com/torvalds/linux/commit/cd21d99e595ec1d8721e1058dcdd4f1f7de1d793
