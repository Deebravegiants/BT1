# [H] NTB: epf: Avoid calling pci_irq_vector() from hardirq context

## Summary
Severity: High
Advisory: CVE-2026-64430
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64430
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

NTB: epf: Avoid calling pci_irq_vector() from hardirq context

ntb_epf_vec_isr() calls pci_irq_vector() in hardirq context to derive
the vector number. pci_irq_vector() calls msi_get_virq() that takes a
mutex and can therefore trigger "scheduling while atomic" splats:

  BUG: scheduling while atomic: kworker/u33:0/55/0x00010001
  ...
  Call trace:
   ...
   schedule+0x38/0x110
   schedule_preempt_disabled+0x28/0x50
   __mutex_lock.constprop.0+0x848/0x908
   __mutex_lock_slowpath+0x18/0x30
   mutex_lock+0x4c/0x60
   msi_domain_get_virq+0xe8/0x138
   pci_irq_vector+0x2c/0x60
   ntb_epf_vec_isr+0x28/0x120 [ntb_hw_epf]
   __handle_irq_event_percpu+0x70/0x3a8
   handle_irq_event+0x48/0x100
   handle_edge_irq+0x100/0x1c8
   ...

Cache the Linux IRQ number for vector 0 when vectors are allocated and
use it as a base in the ISR. Running the ISR in a threaded IRQ handler
would also avoid the problem, but that would be unnecessary here.

## References
- https://git.kernel.org/stable/c/174a97f21bf9c54fa37ec0f321692e862ea130a3
- https://git.kernel.org/stable/c/1dba8444ac0100133d72374634f6d7451fff1ccc
- https://git.kernel.org/stable/c/33bba331a4a5fee8b6026fe72eca13cceeec1b7b
- https://git.kernel.org/stable/c/4dcddc1c794d1c65eda68f1f8dd04a0fecc0870f
- https://git.kernel.org/stable/c/6350df503897d57c5634f71b0767d48c3b837583
- https://git.kernel.org/stable/c/aff271b12a1eb8c8b3da19223ae1a6abe1e8168b
- https://git.kernel.org/stable/c/f71e8d9875069fa73e335f63f02ec6e52e3aaa51
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64430.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64430
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
