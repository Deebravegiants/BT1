# [C] CVE-2019-14196

## Summary
Severity: Critical
Advisory: CVE-2019-14196
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-14196
Type: osv

## Details
An issue was discovered in Das U-Boot through 2019.07. There is an unbounded memcpy with a failed length check at nfs_lookup_reply.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00001.html
- https://blog.semmle.com/uboot-rce-nfs-vulnerability/
- https://gitlab.com/u-boot/u-boot
