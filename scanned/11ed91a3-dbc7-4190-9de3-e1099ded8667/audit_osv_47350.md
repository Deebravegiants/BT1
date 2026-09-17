# [H] CVE-2016-3135

## Summary
Severity: High
Advisory: CVE-2016-3135
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-3135
Type: osv

## Details
Integer overflow in the xt_alloc_table_info function in net/netfilter/x_tables.c in the Linux kernel through 4.5.2 on 32-bit platforms allows local users to gain privileges or cause a denial of service (heap memory corruption) via an IPT_SO_SET_REPLACE setsockopt call.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d157bd761585605b7882935ffb86286919f62ea1
- https://code.google.com/p/google-security-research/issues/detail?id=758
- http://www.securityfocus.com/bid/84305
- http://www.ubuntu.com/usn/USN-3055-1
- http://www.ubuntu.com/usn/USN-3056-1
- http://www.ubuntu.com/usn/USN-3057-1
- http://www.ubuntu.com/usn/USN-2930-3
- http://www.ubuntu.com/usn/USN-2930-1
- http://www.ubuntu.com/usn/USN-2930-2
- http://www.ubuntu.com/usn/USN-3054-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1317386
- https://github.com/torvalds/linux/commit/d157bd761585605b7882935ffb86286919f62ea1
