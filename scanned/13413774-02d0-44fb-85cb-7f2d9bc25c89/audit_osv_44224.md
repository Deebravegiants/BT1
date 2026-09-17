# [H] net: emac: Fix NULL pointer dereference in emac_probe

## Summary
Severity: High
Advisory: CVE-2026-80614
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80614
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: emac: Fix NULL pointer dereference in emac_probe

Move devm_request_irq() after devm_platform_ioremap_resource() so that
dev->emacp is mapped before the interrupt handler can fire.  An early
interrupt hitting emac_irq() would dereference the NULL dev->emacp and
crash.

Also remove redundant error message. devm_platform_ioremap_resource()
already returns an error message with dev_err_probe().

## References
- https://git.kernel.org/stable/c/44068b6863fbda78fc810921ddf61642c377b3ca
- https://git.kernel.org/stable/c/a103cdb0681e7185d1b0a12ce6a7c5416c208ccd
- https://git.kernel.org/stable/c/f623d38fe6c4e8c40b23f42cc6fe6963fa49997b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80614.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80614
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
