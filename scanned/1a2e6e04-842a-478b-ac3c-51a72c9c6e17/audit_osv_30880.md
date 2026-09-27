# [M] gpio: graniterapids: Fix vGPIO driver crash

## Summary
Severity: Medium
Advisory: CVE-2024-56671
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56671
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpio: graniterapids: Fix vGPIO driver crash

Move setting irq_chip.name from probe() function to the initialization
of "irq_chip" struct in order to fix vGPIO driver crash during bootup.

Crash was caused by unauthorized modification of irq_chip.name field
where irq_chip struct was initialized as const.

This behavior is a consequence of suboptimal implementation of
gpio_irq_chip_set_chip(), which should be changed to avoid
casting away const qualifier.

Crash log:
BUG: unable to handle page fault for address: ffffffffc0ba81c0
/#PF: supervisor write access in kernel mode
/#PF: error_code(0x0003) - permissions violation
CPU: 33 UID: 0 PID: 1075 Comm: systemd-udevd Not tainted 6.12.0-rc6-00077-g2e1b3cc9d7f7 #1
Hardware name: Intel Corporation Kaseyville RP/Kaseyville RP, BIOS KVLDCRB1.PGS.0026.D73.2410081258 10/08/2024
RIP: 0010:gnr_gpio_probe+0x171/0x220 [gpio_graniterapids]

## References
- https://git.kernel.org/stable/c/e631cab10c6b287a33c35953e6dbda1f7f89bc1f
- https://git.kernel.org/stable/c/eb9640fd1ce666610b77f5997596e9570a36378f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56671.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56671
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
