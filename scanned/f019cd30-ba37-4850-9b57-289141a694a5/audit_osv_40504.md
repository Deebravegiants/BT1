# [C] serial: 8250_dw: unregister 8250 port if clk_notifier_register() fails

## Summary
Severity: Critical
Advisory: CVE-2026-53384
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53384
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.0.14, >=7.1.0 <7.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: 8250_dw: unregister 8250 port if clk_notifier_register() fails

dw8250_probe() registers the 8250 port via serial8250_register_8250_port()
and then, if the device has a clock, registers a clock notifier. If
clk_notifier_register() fails, probe returns the error but leaves the
8250 port registered. The matching serial8250_unregister_port() lives
in dw8250_remove(), which is not called when probe fails, so the port
slot stays occupied until the device is rebound or the system is
rebooted. The devm-allocated driver data is freed while the port still
references it (via the saved private_data and serial_in/serial_out
callbacks), so any access to that port slot before a rebind is a
use-after-free hazard.

Unregister the port on the clk_notifier_register() error path.

## References
- https://git.kernel.org/stable/c/07ffe414a708ae60551401cec5d727ed156b8caf
- https://git.kernel.org/stable/c/10fc708b4de7f86002d2d735a2dbf3b5b7f65692
- https://git.kernel.org/stable/c/3d205fe80f2181f0109150ad1fa06ee5bc046935
- https://git.kernel.org/stable/c/511d2b92f8d20de04acafab676150d26fb5c67f4
- https://git.kernel.org/stable/c/778b9dda4b24005a27bcd9c35c110bf8d7f259ca
- https://git.kernel.org/stable/c/ccdf4510a3873b14e5e348cdb038717996f09fda
- https://git.kernel.org/stable/c/d72650a4f334581b23a1892b888a4cb1be142f76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53384.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53384
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
