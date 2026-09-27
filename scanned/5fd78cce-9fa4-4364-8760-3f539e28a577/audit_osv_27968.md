# [M] ACPI: processor_idle: Fix memory leak in acpi_processor_power_exit()

## Summary
Severity: Medium
Advisory: CVE-2024-26894
Ecosystem: Linux
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26894
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPI: processor_idle: Fix memory leak in acpi_processor_power_exit()

After unregistering the CPU idle device, the memory associated with
it is not freed, leading to a memory leak:

unreferenced object 0xffff896282f6c000 (size 1024):
  comm "swapper/0", pid 1, jiffies 4294893170
  hex dump (first 32 bytes):
    00 00 00 00 0b 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace (crc 8836a742):
    [<ffffffff993495ed>] kmalloc_trace+0x29d/0x340
    [<ffffffff9972f3b3>] acpi_processor_power_init+0xf3/0x1c0
    [<ffffffff9972d263>] __acpi_processor_start+0xd3/0xf0
    [<ffffffff9972d2bc>] acpi_processor_start+0x2c/0x50
    [<ffffffff99805872>] really_probe+0xe2/0x480
    [<ffffffff99805c98>] __driver_probe_device+0x78/0x160
    [<ffffffff99805daf>] driver_probe_device+0x1f/0x90
    [<ffffffff9980601e>] __driver_attach+0xce/0x1c0
    [<ffffffff99803170>] bus_for_each_dev+0x70/0xc0
    [<ffffffff99804822>] bus_add_driver+0x112/0x210
    [<ffffffff99807245>] driver_register+0x55/0x100
    [<ffffffff9aee4acb>] acpi_processor_driver_init+0x3b/0xc0
    [<ffffffff990012d1>] do_one_initcall+0x41/0x300
    [<ffffffff9ae7c4b0>] kernel_init_freeable+0x320/0x470
    [<ffffffff99b231f6>] kernel_init+0x16/0x1b0
    [<ffffffff99042e6d>] ret_from_fork+0x2d/0x50

Fix this by freeing the CPU idle device after unregistering it.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/1cbaf4c793b0808532f4e7b40bc4be7cec2c78f2
- https://git.kernel.org/stable/c/3d48e5be107429ff5d824e7f2a00d1b610d36fbc
- https://git.kernel.org/stable/c/8d14a4d0afb49a5b8535d414c782bb334860e73e
- https://git.kernel.org/stable/c/c2a30c81bf3cb9033fa9f5305baf7c377075e2e5
- https://git.kernel.org/stable/c/cd5c2d0b09d5b6d3f0a7bbabe6761a4997e9dee9
- https://git.kernel.org/stable/c/d351bcadab6caa6d8ce7159ff4b77e2da35c09fa
- https://git.kernel.org/stable/c/e18afcb7b2a12b635ac10081f943fcf84ddacc51
- https://git.kernel.org/stable/c/ea96bf3f80625cddba1391a87613356b1b45716d
- https://git.kernel.org/stable/c/fad9bcd4d754cc689c19dc04d2c44b82c1a5d6c8
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26894.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26894
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
