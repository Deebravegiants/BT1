# [H] spi: uniphier: Fix completion initialization order before devm_request_irq()

## Summary
Severity: High
Advisory: CVE-2026-72133
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72133
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: uniphier: Fix completion initialization order before devm_request_irq()

The driver calls devm_request_irq() before initializing the completion
used by the interrupt handler. Because the interrupt may occur immediately
after devm_request_irq(), the handler may execute before init_completion().

This may result in calling complete() on an uninitialized completion,
causing undefined behavior. This has been observed with KASAN.

Fix this by initializing the completion before registering the IRQ.

## References
- https://git.kernel.org/stable/c/077a7bc1c32d3da9670c5e282ea3e5ac8a94be59
- https://git.kernel.org/stable/c/49f6705d80b5e6175d8435d9c72b66bd516a8e89
- https://git.kernel.org/stable/c/82a5746c4c9e94f6f816ec7edea6ddc24417c6a5
- https://git.kernel.org/stable/c/8b5798ce0007874c14611b8ee4ce6c749855260e
- https://git.kernel.org/stable/c/b9fcf0db433d79648ace74bc2b8b88f91e306304
- https://git.kernel.org/stable/c/d44b828eb551bd59ba9f22457825cc3db3a39fc1
- https://git.kernel.org/stable/c/f3ad1c87d8201e54b66bd6072442f0b5d5a308ee
- https://git.kernel.org/stable/c/f4bb0a91f7badd6d15ac8d783a1169d9e1e95c17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72133.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72133
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
