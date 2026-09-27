# [M] CVE-2016-6213

## Summary
Severity: Medium
Advisory: CVE-2016-6213
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-28
Source: https://osv.dev/vulnerability/CVE-2016-6213
Type: osv

## Details
fs/namespace.c in the Linux kernel before 4.9 does not restrict how many mounts may exist in a mount namespace, which allows local users to cause a denial of service (memory consumption and deadlock) via MS_BIND mount system calls, as demonstrated by a loop that triggers exponential growth in the number of mounts.

## References
- http://www.securityfocus.com/bid/91754
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://bugzilla.redhat.com/show_bug.cgi?id=1356471
- https://github.com/torvalds/linux/commit/d29216842a85c7970c536108e093963f02714498
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d29216842a85c7970c536108e093963f02714498
- http://www.openwall.com/lists/oss-security/2016/07/13/8
