# [M] CVE-2017-18193

## Summary
Severity: Medium
Advisory: CVE-2017-18193
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-22
Source: https://osv.dev/vulnerability/CVE-2017-18193
Type: osv

## Details
fs/f2fs/extent_cache.c in the Linux kernel before 4.13 mishandles extent trees, which allows local users to cause a denial of service (BUG) via an application with multiple threads.

## References
- https://usn.ubuntu.com/3656-1/
- https://usn.ubuntu.com/3654-1/
- https://usn.ubuntu.com/3654-2/
- https://www.debian.org/security/2018/dsa-4188
- http://www.securityfocus.com/bid/103147
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=dad48e73127ba10279ea33e6dbc8d3905c4d31c0
- https://github.com/torvalds/linux/commit/dad48e73127ba10279ea33e6dbc8d3905c4d31c0
