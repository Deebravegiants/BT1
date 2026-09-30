# [M] CVE-2016-7916

## Summary
Severity: Medium
Advisory: CVE-2016-7916
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2016-7916
Type: osv

## Details
Race condition in the environ_read function in fs/proc/base.c in the Linux kernel before 4.5.4 allows local users to obtain sensitive information from kernel memory by reading a /proc/*/environ file during a process-setup time interval in which environment-variable copying is incomplete.

## References
- http://www.ubuntu.com/usn/USN-3159-1
- http://www.ubuntu.com/usn/USN-3159-2
- http://source.android.com/security/bulletin/2016-11-01.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.4
- http://www.securityfocus.com/bid/94138
- https://bugzilla.kernel.org/show_bug.cgi?id=116461
- https://forums.grsecurity.net/viewtopic.php?f=3&t=4363
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8148a73c9901a8794a50f950083c00ccf97d43b3
- https://github.com/torvalds/linux/commit/8148a73c9901a8794a50f950083c00ccf97d43b3
