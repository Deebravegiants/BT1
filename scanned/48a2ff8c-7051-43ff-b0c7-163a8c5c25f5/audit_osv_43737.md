# [H] serial: amba-pl011: cancel RS485 hrtimers after freeing IRQ

## Summary
Severity: High
Advisory: CVE-2026-74652
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74652
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: amba-pl011: cancel RS485 hrtimers after freeing IRQ

The RS485 trigger hrtimers are embedded in the devm-managed port and can
fire after it is freed. The IRQ handler can arm a timer, so free the IRQ
first and then cancel both timers.

Complete the RS485 stop without arming a timer, and cancel the timers
in remove() for the suspend-then-unbind path, where shutdown is not
called.

This issue was found by an in-house static analysis tool.

## References
- https://git.kernel.org/stable/c/36672c8d7d14e9c43287528455d2c97b526ea6ad
- https://git.kernel.org/stable/c/759ead98a39fb625be302f9aa66290985dcaa325
- https://git.kernel.org/stable/c/e57f0aa5c35be37218ba0e4887b241584dd4b2d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74652.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74652
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
