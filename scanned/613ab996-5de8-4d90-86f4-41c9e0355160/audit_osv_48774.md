# [H] CVE-2018-12930

## Summary
Severity: High
Advisory: CVE-2018-12930
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-28
Source: https://osv.dev/vulnerability/CVE-2018-12930
Type: osv

## Details
ntfs_end_buffer_async_read in the ntfs.ko filesystem driver in the Linux kernel 4.15.0 allows attackers to trigger a stack-based out-of-bounds write and cause a denial of service (kernel oops or panic) or possibly have unspecified other impact via a crafted ntfs filesystem.

## References
- http://www.securityfocus.com/bid/104588
- https://access.redhat.com/errata/RHSA-2019:0641
- https://marc.info/?l=linux-ntfs-dev&m=152413769810234&w=2
- https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1763403
