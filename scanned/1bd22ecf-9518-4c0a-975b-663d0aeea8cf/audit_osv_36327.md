# [H] net: octeon_ep_vf: fix free_irq dev_id mismatch in IRQ rollback

## Summary
Severity: High
Advisory: CVE-2026-23013
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-25
Source: https://osv.dev/vulnerability/CVE-2026-23013
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.67, >=6.13.0 <6.18.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: octeon_ep_vf: fix free_irq dev_id mismatch in IRQ rollback

octep_vf_request_irqs() requests MSI-X queue IRQs with dev_id set to
ioq_vector. If request_irq() fails part-way, the rollback loop calls
free_irq() with dev_id set to 'oct', which does not match the original
dev_id and may leave the irqaction registered.

This can keep IRQ handlers alive while ioq_vector is later freed during
unwind/teardown, leading to a use-after-free or crash when an interrupt
fires.

Fix the error path to free IRQs with the same ioq_vector dev_id used
during request_irq().

## References
- https://git.kernel.org/stable/c/aa05a8371ae4a452df623f7202c72409d3c50e40
- https://git.kernel.org/stable/c/aa4c066229b05fc3d3c5f42693d25b1828533b6e
- https://git.kernel.org/stable/c/f93fc5d12d69012788f82151bee55fce937e1432
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23013.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23013
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
