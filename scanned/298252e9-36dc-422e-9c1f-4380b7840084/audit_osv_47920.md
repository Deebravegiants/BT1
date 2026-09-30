# [M] CVE-2017-14991

## Summary
Severity: Medium
Advisory: CVE-2017-14991
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-10-04
Source: https://osv.dev/vulnerability/CVE-2017-14991
Type: osv

## Details
The sg_ioctl function in drivers/scsi/sg.c in the Linux kernel before 4.13.4 allows local users to obtain sensitive information from uninitialized kernel heap-memory locations via an SG_GET_REQUEST_TABLE ioctl call for /dev/sg0.

## References
- https://usn.ubuntu.com/3754-1/
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.4
- http://www.securityfocus.com/bid/101187
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=3e0097499839e0fe3af380410eababe5a47c4cf9
- https://github.com/torvalds/linux/commit/3e0097499839e0fe3af380410eababe5a47c4cf9
