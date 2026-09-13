# [H] gpio: pca953x: fix pca953x_irq_bus_sync_unlock race

## Summary
Severity: High
Advisory: CVE-2024-42253
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-08
Source: https://osv.dev/vulnerability/CVE-2024-42253
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpio: pca953x: fix pca953x_irq_bus_sync_unlock race

Ensure that `i2c_lock' is held when setting interrupt latch and mask in
pca953x_irq_bus_sync_unlock() in order to avoid races.

The other (non-probe) call site pca953x_gpio_set_multiple() ensures the
lock is held before calling pca953x_write_regs().

The problem occurred when a request raced against irq_bus_sync_unlock()
approximately once per thousand reboots on an i.MX8MP based system.

 * Normal case

   0-0022: write register AI|3a {03,02,00,00,01} Input latch P0
   0-0022: write register AI|49 {fc,fd,ff,ff,fe} Interrupt mask P0
   0-0022: write register AI|08 {ff,00,00,00,00} Output P3
   0-0022: write register AI|12 {fc,00,00,00,00} Config P3

 * Race case

   0-0022: write register AI|08 {ff,00,00,00,00} Output P3
   0-0022: write register AI|08 {03,02,00,00,01} *** Wrong register ***
   0-0022: write register AI|12 {fc,00,00,00,00} Config P3
   0-0022: write register AI|49 {fc,fd,ff,ff,fe} Interrupt mask P0

## References
- https://git.kernel.org/stable/c/58a5c93bd1a6e949267400080f07e57ffe05ec34
- https://git.kernel.org/stable/c/bfc6444b57dc7186b6acc964705d7516cbaf3904
- https://git.kernel.org/stable/c/de7cffa53149c7b48bd1bb29b02390c9f05b7f41
- https://git.kernel.org/stable/c/e2ecdddca80dd845df42376e4b0197fe97018ba2
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42253.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42253
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
