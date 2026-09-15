# [M] platform/x86: dell-uart-backlight: fix serdev race

## Summary
Severity: Medium
Advisory: CVE-2025-21695
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-21695
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: dell-uart-backlight: fix serdev race

The dell_uart_bl_serdev_probe() function calls devm_serdev_device_open()
before setting the client ops via serdev_device_set_client_ops(). This
ordering can trigger a NULL pointer dereference in the serdev controller's
receive_buf handler, as it assumes serdev->ops is valid when
SERPORT_ACTIVE is set.

This is similar to the issue fixed in commit 5e700b384ec1
("platform/chrome: cros_ec_uart: properly fix race condition") where
devm_serdev_device_open() was called before fully initializing the
device.

Fix the race by ensuring client ops are set before enabling the port via
devm_serdev_device_open().

Note, serdev_device_set_baudrate() and serdev_device_set_flow_control()
calls should be after the devm_serdev_device_open() call.

## References
- https://git.kernel.org/stable/c/1b2128aa2d45ab20b22548dcf4b48906298ca7fd
- https://git.kernel.org/stable/c/d3a24d923333f75aaece9acb051d676edc0afb75
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21695.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21695
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
