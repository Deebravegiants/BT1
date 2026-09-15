# [H] clk: imx: Fix an out-of-bounds access in dispmix_csr_clk_dev_data

## Summary
Severity: High
Advisory: CVE-2025-38446
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38446
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: imx: Fix an out-of-bounds access in dispmix_csr_clk_dev_data

When num_parents is 4, __clk_register() occurs an out-of-bounds
when accessing parent_names member. Use ARRAY_SIZE() instead of
hardcode number here.

 BUG: KASAN: global-out-of-bounds in __clk_register+0x1844/0x20d8
 Read of size 8 at addr ffff800086988e78 by task kworker/u24:3/59
  Hardware name: NXP i.MX95 19X19 board (DT)
  Workqueue: events_unbound deferred_probe_work_func
  Call trace:
    dump_backtrace+0x94/0xec
    show_stack+0x18/0x24
    dump_stack_lvl+0x8c/0xcc
    print_report+0x398/0x5fc
    kasan_report+0xd4/0x114
    __asan_report_load8_noabort+0x20/0x2c
    __clk_register+0x1844/0x20d8
    clk_hw_register+0x44/0x110
    __clk_hw_register_mux+0x284/0x3a8
    imx95_bc_probe+0x4f4/0xa70

## References
- https://git.kernel.org/stable/c/a956daad67cec454ee985e103e167711fab5b9b8
- https://git.kernel.org/stable/c/aacc875a448d363332b9df0621dde6d3a225ea9f
- https://git.kernel.org/stable/c/fcee75daecc5234ee3482d8cf3518bf021d8a0a5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38446.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38446
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
