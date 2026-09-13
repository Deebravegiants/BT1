# [M] CVE-2017-5549

## Summary
Severity: Medium
Advisory: CVE-2017-5549
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2017-5549
Type: osv

## Details
The klsi_105_get_line_state function in drivers/usb/serial/kl5kusb105.c in the Linux kernel before 4.9.5 places uninitialized heap-memory contents into a log entry upon a failure to read the line status, which allows local users to obtain sensitive information by reading the log.

## References
- https://usn.ubuntu.com/3754-1/
- http://www.debian.org/security/2017/dsa-3791
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.5
- http://www.securityfocus.com/bid/95715
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=146cc8a17a3b4996f6805ee5c080e7101277c410
- http://www.openwall.com/lists/oss-security/2017/01/21/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1416114
- https://github.com/torvalds/linux/commit/146cc8a17a3b4996f6805ee5c080e7101277c410
