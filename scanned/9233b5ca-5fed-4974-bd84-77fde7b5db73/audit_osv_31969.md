# [M] staging: gpib: Fix Oops after disconnect in agilent usb

## Summary
Severity: Medium
Advisory: CVE-2025-22051
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22051
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: gpib: Fix Oops after disconnect in agilent usb

If the agilent usb dongle is disconnected subsequent calls to the
driver cause a NULL dereference Oops as the bus_interface
is set to NULL on disconnect.

This problem was introduced by setting usb_dev from the bus_interface
for dev_xxx messages.

Previously bus_interface was checked for NULL only in the functions
directly calling usb_fill_bulk_urb or usb_control_msg.

Check for valid bus_interface on all interface entry points
and return -ENODEV if it is NULL.

## References
- https://git.kernel.org/stable/c/50ef6e45bec79da4c5a01fad4dc23466ba255099
- https://git.kernel.org/stable/c/8491e73a5223acb0a4b4d78c3f8b96aa9c5e774d
- https://git.kernel.org/stable/c/e88633705078f40391a9afc6cc8ea3025e6f692b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22051.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22051
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
