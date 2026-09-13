# [C] CVE-2019-14203

## Summary
Severity: Critical
Advisory: CVE-2019-14203
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-14203
Type: osv

## Details
An issue was discovered in Das U-Boot through 2019.07. There is a stack-based buffer overflow in this nfs_handler reply helper function: nfs_mount_reply.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://blog.semmle.com/uboot-rce-nfs-vulnerability/
- https://gitlab.com/u-boot/u-boot
