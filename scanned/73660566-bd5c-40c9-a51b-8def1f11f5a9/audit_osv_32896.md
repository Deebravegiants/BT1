# [H] scsi: megaraid_sas: Fix invalid node index

## Summary
Severity: High
Advisory: CVE-2025-38239
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-07-09
Source: https://osv.dev/vulnerability/CVE-2025-38239
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.143, >=6.2.0 <6.6.96, >=6.7.0 <6.12.36, >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: megaraid_sas: Fix invalid node index

On a system with DRAM interleave enabled, out-of-bound access is
detected:

megaraid_sas 0000:3f:00.0: requested/available msix 128/128 poll_queue 0
------------[ cut here ]------------
UBSAN: array-index-out-of-bounds in ./arch/x86/include/asm/topology.h:72:28
index -1 is out of range for type 'cpumask *[1024]'
dump_stack_lvl+0x5d/0x80
ubsan_epilogue+0x5/0x2b
__ubsan_handle_out_of_bounds.cold+0x46/0x4b
megasas_alloc_irq_vectors+0x149/0x190 [megaraid_sas]
megasas_probe_one.cold+0xa4d/0x189c [megaraid_sas]
local_pci_probe+0x42/0x90
pci_device_probe+0xdc/0x290
really_probe+0xdb/0x340
__driver_probe_device+0x78/0x110
driver_probe_device+0x1f/0xa0
__driver_attach+0xba/0x1c0
bus_for_each_dev+0x8b/0xe0
bus_add_driver+0x142/0x220
driver_register+0x72/0xd0
megasas_init+0xdf/0xff0 [megaraid_sas]
do_one_initcall+0x57/0x310
do_init_module+0x90/0x250
init_module_from_file+0x85/0xc0
idempotent_init_module+0x114/0x310
__x64_sys_finit_module+0x65/0xc0
do_syscall_64+0x82/0x170
entry_SYSCALL_64_after_hwframe+0x76/0x7e

Fix it accordingly.

## References
- https://git.kernel.org/stable/c/074efb35552556a4b3b25eedab076d5dc24a8199
- https://git.kernel.org/stable/c/19a47c966deb36624843b7301f0373a3dc541a05
- https://git.kernel.org/stable/c/752eb816b55adb0673727ba0ed96609a17895654
- https://git.kernel.org/stable/c/bf2c1643abc3b2507d56bb6c22bf9897272f8a35
- https://git.kernel.org/stable/c/f1064b3532192e987ab17be7281d5fee36fd25e1
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38239.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38239
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
