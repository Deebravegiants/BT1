# [M] CVE-2020-11565

## Summary
Severity: Medium
Advisory: CVE-2020-11565
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-04-06
Source: https://osv.dev/vulnerability/CVE-2020-11565
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.6.2. mpol_parse_str in mm/mempolicy.c has a stack-based out-of-bounds write because an empty nodelist is mishandled during mount option parsing, aka CID-aa9f7d5172fa. NOTE: Someone in the security community disagrees that this is a vulnerability because the issue “is a bug in parsing mount options which can only be specified by a privileged user, so triggering the bug does not grant any powers not already held.”

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://usn.ubuntu.com/4369-1/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://usn.ubuntu.com/4363-1/
- https://www.debian.org/security/2020/dsa-4667
- https://www.debian.org/security/2020/dsa-4698
- https://usn.ubuntu.com/4364-1/
- https://usn.ubuntu.com/4367-1/
- https://usn.ubuntu.com/4368-1/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=aa9f7d5172fac9bf1f09e678c35e287a40a7b7dd
- https://github.com/torvalds/linux/commit/aa9f7d5172fac9bf1f09e678c35e287a40a7b7dd
