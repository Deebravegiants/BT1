# [M] usb: cdns3: Put the cdns set active part outside the spin lock

## Summary
Severity: Medium
Advisory: CVE-2023-53287
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53287
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.15.133, >=5.16.0 <6.1.55, >=6.2.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: cdns3: Put the cdns set active part outside the spin lock

The device may be scheduled during the resume process,
so this cannot appear in atomic operations. Since
pm_runtime_set_active will resume suppliers, put set
active outside the spin lock, which is only used to
protect the struct cdns data structure, otherwise the
kernel will report the following warning:

  BUG: sleeping function called from invalid context at drivers/base/power/runtime.c:1163
  in_atomic(): 1, irqs_disabled(): 0, non_block: 0, pid: 651, name: sh
  preempt_count: 1, expected: 0
  RCU nest depth: 0, expected: 0
  CPU: 0 PID: 651 Comm: sh Tainted: G        WC         6.1.20 #1
  Hardware name: Freescale i.MX8QM MEK (DT)
  Call trace:
    dump_backtrace.part.0+0xe0/0xf0
    show_stack+0x18/0x30
    dump_stack_lvl+0x64/0x80
    dump_stack+0x1c/0x38
    __might_resched+0x1fc/0x240
    __might_sleep+0x68/0xc0
    __pm_runtime_resume+0x9c/0xe0
    rpm_get_suppliers+0x68/0x1b0
    __pm_runtime_set_status+0x298/0x560
    cdns_resume+0xb0/0x1c0
    cdns3_controller_resume.isra.0+0x1e0/0x250
    cdns3_plat_resume+0x28/0x40

## References
- https://git.kernel.org/stable/c/2319b9c87fe243327285f2fefd7374ffd75a65fc
- https://git.kernel.org/stable/c/bbc9c3652708108738009e096d608ece3cd9fa8a
- https://git.kernel.org/stable/c/c861a61be6d30538ebcf7fcab1d43f244e298840
- https://git.kernel.org/stable/c/d3f372ec95b89776f72d5c9a475424e27734c223
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53287.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53287
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
