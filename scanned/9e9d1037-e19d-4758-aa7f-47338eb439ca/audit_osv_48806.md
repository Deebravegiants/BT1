# [M] CVE-2018-14609

## Summary
Severity: Medium
Advisory: CVE-2018-14609
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2018-14609
Type: osv

## Details
An issue was discovered in the Linux kernel through 4.17.10. There is an invalid pointer dereference in __del_reloc_root() in fs/btrfs/relocation.c when mounting a crafted btrfs image, related to removing reloc rb_trees when reloc control has not been initialized.

## References
- https://usn.ubuntu.com/4118-1/
- https://usn.ubuntu.com/4094-1/
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://usn.ubuntu.com/3821-1/
- https://www.debian.org/security/2018/dsa-4308
- https://usn.ubuntu.com/3821-2/
- http://www.securityfocus.com/bid/104917
- https://bugzilla.kernel.org/show_bug.cgi?id=199833
- https://patchwork.kernel.org/patch/10500521/
