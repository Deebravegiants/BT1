# [M] CVE-2018-12929

## Summary
Severity: Medium
Advisory: CVE-2018-12929
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-28
Source: https://osv.dev/vulnerability/CVE-2018-12929
Type: osv

## Details
ntfs_read_locked_inode in the ntfs.ko filesystem driver in the Linux kernel 4.15.0 allows attackers to trigger a use-after-free read and possibly cause a denial of service (kernel oops or panic) via a crafted ntfs filesystem.

## References
- https://access.redhat.com/errata/RHSA-2019:0641
- https://marc.info/?l=linux-ntfs-dev&m=152413769810234&w=2
- http://www.securityfocus.com/bid/104588
- https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1763403
