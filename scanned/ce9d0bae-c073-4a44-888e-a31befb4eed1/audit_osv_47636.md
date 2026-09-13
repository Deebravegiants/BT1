# [H] CVE-2016-9754

## Summary
Severity: High
Advisory: CVE-2016-9754
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-05
Source: https://osv.dev/vulnerability/CVE-2016-9754
Type: osv

## Details
The ring_buffer_resize function in kernel/trace/ring_buffer.c in the profiling subsystem in the Linux kernel before 4.6.1 mishandles certain integer calculations, which allows local users to gain privileges by writing to the /sys/kernel/debug/tracing/buffer_size_kb file.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.1
- http://www.securityfocus.com/bid/95278
- https://source.android.com/security/bulletin/2017-01-01.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=59643d1535eb220668692a5359de22545af579f6
- https://github.com/torvalds/linux/commit/59643d1535eb220668692a5359de22545af579f6
