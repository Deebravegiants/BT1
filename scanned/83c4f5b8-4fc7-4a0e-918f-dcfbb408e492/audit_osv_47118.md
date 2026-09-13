# [H] CVE-2015-8962

## Summary
Severity: High
Advisory: CVE-2015-8962
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2015-8962
Type: osv

## Details
Double free vulnerability in the sg_common_write function in drivers/scsi/sg.c in the Linux kernel before 4.4 allows local users to gain privileges or cause a denial of service (memory corruption and system crash) by detaching a device during an SG_IO ioctl call.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f3951a3709ff50990bf3e188c27d346792103432
- http://www.securityfocus.com/bid/94187
- https://github.com/torvalds/linux/commit/f3951a3709ff50990bf3e188c27d346792103432
- https://source.android.com/security/bulletin/2016-11-01.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f3951a3709ff50990bf3e188c27d346792103432
- https://github.com/torvalds/linux/commit/f3951a3709ff50990bf3e188c27d346792103432
