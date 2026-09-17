# [M] irqchip/gic-v3-its: Don't enable interrupts in its_irq_set_vcpu_affinity()

## Summary
Severity: Medium
Advisory: CVE-2024-57949
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-09
Source: https://osv.dev/vulnerability/CVE-2024-57949
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.127, >=6.2.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/gic-v3-its: Don't enable interrupts in its_irq_set_vcpu_affinity()

The following call-chain leads to enabling interrupts in a nested interrupt
disabled section:

irq_set_vcpu_affinity()
  irq_get_desc_lock()
     raw_spin_lock_irqsave()   <--- Disable interrupts
  its_irq_set_vcpu_affinity()
     guard(raw_spinlock_irq)   <--- Enables interrupts when leaving the guard()
  irq_put_desc_unlock()        <--- Warns because interrupts are enabled

This was broken in commit b97e8a2f7130, which replaced the original
raw_spin_[un]lock() pair with guard(raw_spinlock_irq).

Fix the issue by using guard(raw_spinlock).

[ tglx: Massaged change log ]

## References
- https://git.kernel.org/stable/c/35cb2c6ce7da545f3b5cb1e6473ad7c3a6f08310
- https://git.kernel.org/stable/c/6c84ff2e788fce0099ee3e71a3ed258b1ca1a223
- https://git.kernel.org/stable/c/93955a7788121ab5a0f7f27e988b2ed1135a4866
- https://git.kernel.org/stable/c/d7b0e89610dd45ac6cf0d6f99bfa9ccc787db344
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57949.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57949
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
