# [H] CVE-2017-18255

## Summary
Severity: High
Advisory: CVE-2017-18255
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-31
Source: https://osv.dev/vulnerability/CVE-2017-18255
Type: osv

## Details
The perf_cpu_time_max_percent_handler function in kernel/events/core.c in the Linux kernel before 4.11 allows local users to cause a denial of service (integer overflow) or possibly have unspecified other impact via a large value, as demonstrated by an incorrect sample-rate calculation.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3696-1/
- https://usn.ubuntu.com/3696-2/
- https://usn.ubuntu.com/3754-1/
- http://www.securityfocus.com/bid/103607
- https://github.com/torvalds/linux/commit/1572e45a924f254d9570093abde46430c3172e3d
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1572e45a924f254d9570093abde46430c3172e3d
