# [M] CVE-2018-12928

## Summary
Severity: Medium
Advisory: CVE-2018-12928
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-28
Source: https://osv.dev/vulnerability/CVE-2018-12928
Type: osv

## Details
In the Linux kernel 4.15.0, a NULL pointer dereference was discovered in hfs_ext_read_extent in hfs.ko. This can occur during a mount of a crafted hfs filesystem.

## References
- http://www.securityfocus.com/bid/104593
- https://marc.info/?l=linux-fsdevel&m=152407263325766&w=2
- https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1763384
