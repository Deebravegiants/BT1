# [M] powerpc/pseries/iommu: LPAR panics during boot up with a frozen PE

## Summary
Severity: Medium
Advisory: CVE-2024-36926
Ecosystem: Linux
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36926
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/pseries/iommu: LPAR panics during boot up with a frozen PE

At the time of LPAR boot up, partition firmware provides Open Firmware
property ibm,dma-window for the PE. This property is provided on the PCI
bus the PE is attached to.

There are execptions where the partition firmware might not provide this
property for the PE at the time of LPAR boot up. One of the scenario is
where the firmware has frozen the PE due to some error condition. This
PE is frozen for 24 hours or unless the whole system is reinitialized.

Within this time frame, if the LPAR is booted, the frozen PE will be
presented to the LPAR but ibm,dma-window property could be missing.

Today, under these circumstances, the LPAR oopses with NULL pointer
dereference, when configuring the PCI bus the PE is attached to.

  BUG: Kernel NULL pointer dereference on read at 0x000000c8
  Faulting instruction address: 0xc0000000001024c0
  Oops: Kernel access of bad area, sig: 7 [#1]
  LE PAGE_SIZE=64K MMU=Radix SMP NR_CPUS=2048 NUMA pSeries
  Modules linked in:
  Supported: Yes
  CPU: 0 PID: 1 Comm: swapper/0 Not tainted 6.4.0-150600.9-default #1
  Hardware name: IBM,9043-MRX POWER10 (raw) 0x800200 0xf000006 of:IBM,FW1060.00 (NM1060_023) hv:phyp pSeries
  NIP:  c0000000001024c0 LR: c0000000001024b0 CTR: c000000000102450
  REGS: c0000000037db5c0 TRAP: 0300   Not tainted  (6.4.0-150600.9-default)
  MSR:  8000000002009033 <SF,VEC,EE,ME,IR,DR,RI,LE>  CR: 28000822  XER: 00000000
  CFAR: c00000000010254c DAR: 00000000000000c8 DSISR: 00080000 IRQMASK: 0
  ...
  NIP [c0000000001024c0] pci_dma_bus_setup_pSeriesLP+0x70/0x2a0
  LR [c0000000001024b0] pci_dma_bus_setup_pSeriesLP+0x60/0x2a0
  Call Trace:
    pci_dma_bus_setup_pSeriesLP+0x60/0x2a0 (unreliable)
    pcibios_setup_bus_self+0x1c0/0x370
    __of_scan_bus+0x2f8/0x330
    pcibios_scan_phb+0x280/0x3d0
    pcibios_init+0x88/0x12c
    do_one_initcall+0x60/0x320
    kernel_init_freeable+0x344/0x3e4
    kernel_init+0x34/0x1d0
    ret_from_kernel_user_thread+0x14/0x1c

## References
- https://git.kernel.org/stable/c/2bed905a72485a2b79a001bd7e66c750942d2155
- https://git.kernel.org/stable/c/49a940dbdc3107fecd5e6d3063dc07128177e058
- https://git.kernel.org/stable/c/7fb5793c53f8c024e3eae9f0d44eb659aed833c4
- https://git.kernel.org/stable/c/802b13b79ab1fef66c6852fc745cf197dca0cb15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36926.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36926
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
