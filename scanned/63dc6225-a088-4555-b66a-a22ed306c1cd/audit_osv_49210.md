# [M] CVE-2018-5953

## Summary
Severity: Medium
Advisory: CVE-2018-5953
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-07
Source: https://osv.dev/vulnerability/CVE-2018-5953
Type: osv

## Details
The swiotlb_print_info function in lib/swiotlb.c in the Linux kernel through 4.14.14 allows local users to obtain sensitive address information by reading dmesg data from a "software IO TLB" printk call.

## References
- https://github.com/johnsonwangqize/cve-linux/blob/master/%20CVE-2018-5953.md
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- http://www.securityfocus.com/bid/105045
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=7d63fb3af87aa67aa7d24466e792f9d7c57d8e79
