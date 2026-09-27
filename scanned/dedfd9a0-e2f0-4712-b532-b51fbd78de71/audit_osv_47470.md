# [M] CVE-2016-6156

## Summary
Severity: Medium
Advisory: CVE-2016-6156
CVSS: 5.1 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6156
Type: osv

## Details
Race condition in the ec_device_ioctl_xcmd function in drivers/platform/chrome/cros_ec_dev.c in the Linux kernel before 4.7 allows local users to cause a denial of service (out-of-bounds array access) by changing a certain size value, aka a "double fetch" vulnerability.

## References
- http://www.securityfocus.com/bid/91553
- http://seclists.org/bugtraq/2016/Jul/20
- https://bugzilla.kernel.org/show_bug.cgi?id=120131
- https://bugzilla.redhat.com/show_bug.cgi?id=1353490
- https://github.com/torvalds/linux/commit/096cdc6f52225835ff503f987a0d68ef770bb78e
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=096cdc6f52225835ff503f987a0d68ef770bb78e
