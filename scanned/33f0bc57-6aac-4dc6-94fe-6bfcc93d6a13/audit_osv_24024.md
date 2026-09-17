# [M] ACPI: APEI: Fix integer overflow in ghes_estatus_pool_init()

## Summary
Severity: Medium
Advisory: CVE-2022-49885
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49885
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPI: APEI: Fix integer overflow in ghes_estatus_pool_init()

Change num_ghes from int to unsigned int, preventing an overflow
and causing subsequent vmalloc() to fail.

The overflow happens in ghes_estatus_pool_init() when calculating
len during execution of the statement below as both multiplication
operands here are signed int:

len += (num_ghes * GHES_ESOURCE_PREALLOC_MAX_SIZE);

The following call trace is observed because of this bug:

[    9.317108] swapper/0: vmalloc error: size 18446744071562596352, exceeds total pages, mode:0xcc0(GFP_KERNEL), nodemask=(null),cpuset=/,mems_allowed=0-1
[    9.317131] Call Trace:
[    9.317134]  <TASK>
[    9.317137]  dump_stack_lvl+0x49/0x5f
[    9.317145]  dump_stack+0x10/0x12
[    9.317146]  warn_alloc.cold+0x7b/0xdf
[    9.317150]  ? __device_attach+0x16a/0x1b0
[    9.317155]  __vmalloc_node_range+0x702/0x740
[    9.317160]  ? device_add+0x17f/0x920
[    9.317164]  ? dev_set_name+0x53/0x70
[    9.317166]  ? platform_device_add+0xf9/0x240
[    9.317168]  __vmalloc_node+0x49/0x50
[    9.317170]  ? ghes_estatus_pool_init+0x43/0xa0
[    9.317176]  vmalloc+0x21/0x30
[    9.317177]  ghes_estatus_pool_init+0x43/0xa0
[    9.317179]  acpi_hest_init+0x129/0x19c
[    9.317185]  acpi_init+0x434/0x4a4
[    9.317188]  ? acpi_sleep_proc_init+0x2a/0x2a
[    9.317190]  do_one_initcall+0x48/0x200
[    9.317195]  kernel_init_freeable+0x221/0x284
[    9.317200]  ? rest_init+0xe0/0xe0
[    9.317204]  kernel_init+0x1a/0x130
[    9.317205]  ret_from_fork+0x22/0x30
[    9.317208]  </TASK>

[ rjw: Subject and changelog edits ]

## References
- https://git.kernel.org/stable/c/43d2748394c3feb86c0c771466f5847e274fc043
- https://git.kernel.org/stable/c/4c10c854113720cbfe75d4f51db79b700a629e73
- https://git.kernel.org/stable/c/9edf20e5a1d805855e78f241cf221d741b50d482
- https://git.kernel.org/stable/c/c50ec15725e005e9fb20bce69b6c23b135a4a9b7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49885.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49885
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
