# [H] CVE-2016-7912

## Summary
Severity: High
Advisory: CVE-2016-7912
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2016-7912
Type: osv

## Details
Use-after-free vulnerability in the ffs_user_copy_worker function in drivers/usb/gadget/function/f_fs.c in the Linux kernel before 4.5.3 allows local users to gain privileges by accessing an I/O data structure after a certain callback call.

## References
- http://source.android.com/security/bulletin/2016-11-01.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.3
- http://www.securityfocus.com/bid/94197
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=38740a5b87d53ceb89eb2c970150f6e94e00373a
- https://github.com/torvalds/linux/commit/38740a5b87d53ceb89eb2c970150f6e94e00373a
