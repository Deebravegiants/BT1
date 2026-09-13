# [M] CVE-2018-10888

## Summary
Severity: Medium
Advisory: CVE-2018-10888
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-10
Source: https://osv.dev/vulnerability/CVE-2018-10888
Type: osv

## Details
A flaw was found in libgit2 before version 0.27.3. A missing check in git_delta_apply function in delta.c file, may lead to an out-of-bound read while reading a binary delta file. An attacker may use this flaw to cause a Denial of Service.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00024.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00031.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1598024
- https://github.com/libgit2/libgit2/commit/9844d38bed10e9ff17174434b3421b227ae710f3
- https://github.com/libgit2/libgit2/releases/tag/v0.27.3
