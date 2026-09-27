# [H] KVM: x86: Nullify irqfd->producer if updating IRTE for bypass fails

## Summary
Severity: High
Advisory: CVE-2026-72283
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72283
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: Nullify irqfd->producer if updating IRTE for bypass fails

Nullify irqfd->producer if updating the IRTE for bypass fails, as leaving a
dangling pointer will result in a use-after-free if the irqfd is reachable
through KVM's routing, but the producer is freed separately.  E.g. for VFIO
PCI, the producer is embedded in struct "vfio_pci_irq_ctx" and freed when
the vector is disabled, which can happen independent of routing updates.

[sean: drop PPC change, massage changelog]

## References
- https://git.kernel.org/stable/c/d1379888cc4230bac647ec24ab83306afbd03e88
- https://git.kernel.org/stable/c/d5560b6569cd05ba72c6b33427fbabc6ec46b8cf
- https://git.kernel.org/stable/c/ed446e8aa894883c08892cfee69782fdf8f6c3ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72283.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72283
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
