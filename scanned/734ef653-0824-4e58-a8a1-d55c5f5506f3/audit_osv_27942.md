# [H] RDMA/irdma: Fix KASAN issue with tasklet

## Summary
Severity: High
Advisory: CVE-2024-26838
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26838
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/irdma: Fix KASAN issue with tasklet

KASAN testing revealed the following issue assocated with freeing an IRQ.

[50006.466686] Call Trace:
[50006.466691]  <IRQ>
[50006.489538]  dump_stack+0x5c/0x80
[50006.493475]  print_address_description.constprop.6+0x1a/0x150
[50006.499872]  ? irdma_sc_process_ceq+0x483/0x790 [irdma]
[50006.505742]  ? irdma_sc_process_ceq+0x483/0x790 [irdma]
[50006.511644]  kasan_report.cold.11+0x7f/0x118
[50006.516572]  ? irdma_sc_process_ceq+0x483/0x790 [irdma]
[50006.522473]  irdma_sc_process_ceq+0x483/0x790 [irdma]
[50006.528232]  irdma_process_ceq+0xb2/0x400 [irdma]
[50006.533601]  ? irdma_hw_flush_wqes_callback+0x370/0x370 [irdma]
[50006.540298]  irdma_ceq_dpc+0x44/0x100 [irdma]
[50006.545306]  tasklet_action_common.isra.14+0x148/0x2c0
[50006.551096]  __do_softirq+0x1d0/0xaf8
[50006.555396]  irq_exit_rcu+0x219/0x260
[50006.559670]  irq_exit+0xa/0x20
[50006.563320]  smp_apic_timer_interrupt+0x1bf/0x690
[50006.568645]  apic_timer_interrupt+0xf/0x20
[50006.573341]  </IRQ>

The issue is that a tasklet could be pending on another core racing
the delete of the irq.

Fix by insuring any scheduled tasklet is killed after deleting the
irq.

## References
- https://git.kernel.org/stable/c/0ae8ad0013978f7471f22bcf45b027393e87f5dc
- https://git.kernel.org/stable/c/635d79aa477f9912e602feb5498bdd51fb9cb824
- https://git.kernel.org/stable/c/b2e4a5266e3d133b4c7f0e43bf40d13ce14fd1aa
- https://git.kernel.org/stable/c/bd97cea7b18a0a553773af806dfbfac27a7c4acb
- https://git.kernel.org/stable/c/c6f1ca235f68b22b3e691b2ea87ac285e5946848
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26838.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26838
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
