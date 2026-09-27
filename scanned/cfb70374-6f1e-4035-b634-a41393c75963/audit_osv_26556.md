# [M] of/fdt: run soc memory setup when early_init_dt_scan_memory fails

## Summary
Severity: Medium
Advisory: CVE-2023-53341
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53341
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.0.19, >=6.1.0 <6.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

of/fdt: run soc memory setup when early_init_dt_scan_memory fails

If memory has been found early_init_dt_scan_memory now returns 1. If
it hasn't found any memory it will return 0, allowing other memory
setup mechanisms to carry on.

Previously early_init_dt_scan_memory always returned 0 without
distinguishing between any kind of memory setup being done or not. Any
code path after the early_init_dt_scan memory call in the ramips
plat_mem_setup code wouldn't be executed anymore. Making
early_init_dt_scan_memory the only way to initialize the memory.

Some boards, including my mt7621 based Cudy X6 board, depend on memory
initialization being done via the soc_info.mem_detect function
pointer. Those wouldn't be able to obtain memory and panic the kernel
during early bootup with the message "early_init_dt_alloc_memory_arch:
Failed to allocate 12416 bytes align=0x40".

## References
- https://git.kernel.org/stable/c/04836fc5b720dfa32ff781383d84f63019abf9b9
- https://git.kernel.org/stable/c/2a12187d5853d9fd5102278cecef7dac7c8ce7ea
- https://git.kernel.org/stable/c/c4849f18185fd4e93b04cd45552f8d68c0240e21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53341.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53341
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
