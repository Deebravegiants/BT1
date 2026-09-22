# [H] powerpc/iommu: Fix notifiers being shared by PCI and VIO buses

## Summary
Severity: High
Advisory: CVE-2023-54095
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54095
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/iommu: Fix notifiers being shared by PCI and VIO buses

fail_iommu_setup() registers the fail_iommu_bus_notifier struct to both
PCI and VIO buses.  struct notifier_block is a linked list node, so this
causes any notifiers later registered to either bus type to also be
registered to the other since they share the same node.

This causes issues in (at least) the vgaarb code, which registers a
notifier for PCI buses.  pci_notify() ends up being called on a vio
device, converted with to_pci_dev() even though it's not a PCI device,
and finally makes a bad access in vga_arbiter_add_pci_device() as
discovered with KASAN:

 BUG: KASAN: slab-out-of-bounds in vga_arbiter_add_pci_device+0x60/0xe00
 Read of size 4 at addr c000000264c26fdc by task swapper/0/1

 Call Trace:
   dump_stack_lvl+0x1bc/0x2b8 (unreliable)
   print_report+0x3f4/0xc60
   kasan_report+0x244/0x698
   __asan_load4+0xe8/0x250
   vga_arbiter_add_pci_device+0x60/0xe00
   pci_notify+0x88/0x444
   notifier_call_chain+0x104/0x320
   blocking_notifier_call_chain+0xa0/0x140
   device_add+0xac8/0x1d30
   device_register+0x58/0x80
   vio_register_device_node+0x9ac/0xce0
   vio_bus_scan_register_devices+0xc4/0x13c
   __machine_initcall_pseries_vio_device_init+0x94/0xf0
   do_one_initcall+0x12c/0xaa8
   kernel_init_freeable+0xa48/0xba8
   kernel_init+0x64/0x400
   ret_from_kernel_thread+0x5c/0x64

Fix this by creating separate notifier_block structs for each bus type.

[mpe: Add #ifdef to fix CONFIG_IBMVIO=n build]

## References
- https://git.kernel.org/stable/c/075a4dcdbc9a5ea793cb8ec8b78a6c0b7636fd52
- https://git.kernel.org/stable/c/65bf8a196ba25cf65a858b5bb8de80f0aad76691
- https://git.kernel.org/stable/c/6670c65bf863cd0d44ca24d4c10ef6755b8d9529
- https://git.kernel.org/stable/c/a9ddbfed53465bc7c411231db32a488066c0c1be
- https://git.kernel.org/stable/c/c37b6908f7b2bd24dcaaf14a180e28c9132b9c58
- https://git.kernel.org/stable/c/c46af58588253e5e4063bb5ddc78cd12fdf9e55d
- https://git.kernel.org/stable/c/dc0d107e624ca96aef6dd8722eb33ba3a6d157b0
- https://git.kernel.org/stable/c/f08944e3c6962b00827de7263a9e20688e79ad84
- https://git.kernel.org/stable/c/f17d5efaafba3d5f02f0373f7c5f44711d676f3e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54095.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54095
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
