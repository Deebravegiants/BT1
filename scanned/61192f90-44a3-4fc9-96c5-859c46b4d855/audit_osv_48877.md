# [M] CVE-2018-16862

## Summary
Severity: Medium
Advisory: CVE-2018-16862
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-11-26
Source: https://osv.dev/vulnerability/CVE-2018-16862
Type: osv

## Details
A security flaw was found in the Linux kernel in a way that the cleancache subsystem clears an inode after the final file truncation (removal). The new file created with the same inode may contain leftover pages from cleancache and the old file data instead of the new one.

## References
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4118-1/
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://usn.ubuntu.com/3879-2/
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://seclists.org/oss-sec/2018/q4/169
- https://usn.ubuntu.com/3879-1/
- http://www.securityfocus.com/bid/106009
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16862
- https://lore.kernel.org/patchwork/patch/1011367/
