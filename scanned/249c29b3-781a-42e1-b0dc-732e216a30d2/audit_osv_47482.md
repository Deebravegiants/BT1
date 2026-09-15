# [H] CVE-2016-6516

## Summary
Severity: High
Advisory: CVE-2016-6516
CVSS: 7.4 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6516
Type: osv

## Details
Race condition in the ioctl_file_dedupe_range function in fs/ioctl.c in the Linux kernel through 4.7 allows local users to cause a denial of service (heap-based buffer overflow) or possibly gain privileges by changing a certain count value, aka a "double fetch" vulnerability.

## References
- http://www.securityfocus.com/bid/92259
- http://www.openwall.com/lists/oss-security/2016/07/31/6
- https://bugzilla.redhat.com/show_bug.cgi?id=1362457
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=10eec60ce79187686e052092e5383c99b4420a20
- https://github.com/torvalds/linux/commit/10eec60ce79187686e052092e5383c99b4420a20
