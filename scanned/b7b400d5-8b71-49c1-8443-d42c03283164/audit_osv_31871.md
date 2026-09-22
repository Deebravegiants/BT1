# [H] cdx: Fix possible UAF error in driver_override_show()

## Summary
Severity: High
Advisory: CVE-2025-21915
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21915
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

cdx: Fix possible UAF error in driver_override_show()

Fixed a possible UAF problem in driver_override_show() in drivers/cdx/cdx.c

This function driver_override_show() is part of DEVICE_ATTR_RW, which
includes both driver_override_show() and driver_override_store().
These functions can be executed concurrently in sysfs.

The driver_override_store() function uses driver_set_override() to
update the driver_override value, and driver_set_override() internally
locks the device (device_lock(dev)). If driver_override_show() reads
cdx_dev->driver_override without locking, it could potentially access
a freed pointer if driver_override_store() frees the string
concurrently. This could lead to printing a kernel address, which is a
security risk since DEVICE_ATTR can be read by all users.

Additionally, a similar pattern is used in drivers/amba/bus.c, as well
as many other bus drivers, where device_lock() is taken in the show
function, and it has been working without issues.

This potential bug was detected by our experimental static analysis
tool, which analyzes locking APIs and paired functions to identify
data races and atomicity violations.

## References
- https://git.kernel.org/stable/c/0439d541aa8d3444ad41c39e39eb71acb57acde3
- https://git.kernel.org/stable/c/8473135f89c0949436a22adb05b8cece2fb3da91
- https://git.kernel.org/stable/c/91d44c1afc61a2fec37a9c7a3485368309391e0b
- https://git.kernel.org/stable/c/d7b339bbc887bcfc1a5b620bfc70c6fbb8f733bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21915.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21915
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
