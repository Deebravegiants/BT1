# [M] cxl/region: Fix region HPA ordering validation

## Summary
Severity: Medium
Advisory: CVE-2022-49894
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49894
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

cxl/region: Fix region HPA ordering validation

Some regions may not have any address space allocated. Skip them when
validating HPA order otherwise a crash like the following may result:

 devm_cxl_add_region: cxl_acpi cxl_acpi.0: decoder3.4: created region9
 BUG: kernel NULL pointer dereference, address: 0000000000000000
 [..]
 RIP: 0010:store_targetN+0x655/0x1740 [cxl_core]
 [..]
 Call Trace:
  <TASK>
  kernfs_fop_write_iter+0x144/0x200
  vfs_write+0x24a/0x4d0
  ksys_write+0x69/0xf0
  do_syscall_64+0x3a/0x90

store_targetN+0x655/0x1740:
alloc_region_ref at drivers/cxl/core/region.c:676
(inlined by) cxl_port_attach_region at drivers/cxl/core/region.c:850
(inlined by) cxl_region_attach at drivers/cxl/core/region.c:1290
(inlined by) attach_target at drivers/cxl/core/region.c:1410
(inlined by) store_targetN at drivers/cxl/core/region.c:1453

## References
- https://git.kernel.org/stable/c/12316b9f7c18138ae656050cfd716728e27b7e2f
- https://git.kernel.org/stable/c/a90accb358ae33ea982a35595573f7a045993f8b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49894.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49894
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
