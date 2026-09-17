# [C] CVE-2019-14195

## Summary
Severity: Critical
Advisory: CVE-2019-14195
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-14195
Type: osv

## Details
An issue was discovered in Das U-Boot through 2019.07. There is an unbounded memcpy with unvalidated length at nfs_readlink_reply in the "else" block after calculating the new path length.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://blog.semmle.com/uboot-rce-nfs-vulnerability/
- https://gitlab.com/u-boot/u-boot
