# [H] CVE-2019-13105

## Summary
Severity: High
Advisory: CVE-2019-13105
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-06
Source: https://osv.dev/vulnerability/CVE-2019-13105
Type: osv

## Details
Das U-Boot versions 2019.07-rc1 through 2019.07-rc4 can double-free a cached block of data when listing files in a crafted ext4 filesystem.

## References
- https://gist.github.com/deephooloovoo/d91b81a1674b4750e662dfae93804d75
- https://github.com/u-boot/u-boot/commits/master
- https://lists.denx.de/pipermail/u-boot/2019-July/375513.html
