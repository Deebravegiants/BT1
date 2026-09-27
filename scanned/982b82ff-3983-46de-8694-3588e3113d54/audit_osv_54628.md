# [M] CVE-2024-2312

## Summary
Severity: Medium
Advisory: CVE-2024-2312
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-05
Source: https://osv.dev/vulnerability/CVE-2024-2312
Type: osv

## Details
GRUB2 does not call the module fini functions on exit, leading to Debian/Ubuntu's peimage GRUB2 module leaving UEFI system table hooks after exit. This lead to a use-after-free condition, and could possibly lead to secure boot bypass.

## References
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-2312
- https://security.netapp.com/advisory/ntap-20240426-0003/
- https://bugs.launchpad.net/ubuntu/+source/grub2-unsigned/+bug/2054127
