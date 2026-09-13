# [M] ice: fix memory leak in aRFS after reset

## Summary
Severity: Medium
Advisory: CVE-2025-21981
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21981
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.84, >=6.7.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix memory leak in aRFS after reset

Fix aRFS (accelerated Receive Flow Steering) structures memory leak by
adding a checker to verify if aRFS memory is already allocated while
configuring VSI. aRFS objects are allocated in two cases:
- as part of VSI initialization (at probe), and
- as part of reset handling

However, VSI reconfiguration executed during reset involves memory
allocation one more time, without prior releasing already allocated
resources. This led to the memory leak with the following signature:

[root@os-delivery ~]# cat /sys/kernel/debug/kmemleak
unreferenced object 0xff3c1ca7252e6000 (size 8192):
  comm "kworker/0:0", pid 8, jiffies 4296833052
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace (crc 0):
    [<ffffffff991ec485>] __kmalloc_cache_noprof+0x275/0x340
    [<ffffffffc0a6e06a>] ice_init_arfs+0x3a/0xe0 [ice]
    [<ffffffffc09f1027>] ice_vsi_cfg_def+0x607/0x850 [ice]
    [<ffffffffc09f244b>] ice_vsi_setup+0x5b/0x130 [ice]
    [<ffffffffc09c2131>] ice_init+0x1c1/0x460 [ice]
    [<ffffffffc09c64af>] ice_probe+0x2af/0x520 [ice]
    [<ffffffff994fbcd3>] local_pci_probe+0x43/0xa0
    [<ffffffff98f07103>] work_for_cpu_fn+0x13/0x20
    [<ffffffff98f0b6d9>] process_one_work+0x179/0x390
    [<ffffffff98f0c1e9>] worker_thread+0x239/0x340
    [<ffffffff98f14abc>] kthread+0xcc/0x100
    [<ffffffff98e45a6d>] ret_from_fork+0x2d/0x50
    [<ffffffff98e083ba>] ret_from_fork_asm+0x1a/0x30
    ...

## References
- https://git.kernel.org/stable/c/23d97f18901ef5e4e264e3b1777fe65c760186b5
- https://git.kernel.org/stable/c/3b27e6e10a32589fcd293b8933ab6de9387a460e
- https://git.kernel.org/stable/c/5d30d256661fc11b6e73fac6c3783a702e1006a3
- https://git.kernel.org/stable/c/78f3d64b30210c0e521c59357431aca14024cb79
- https://git.kernel.org/stable/c/e6902101f34f098af59b0d1d8cf90c4124c02c6a
- https://git.kernel.org/stable/c/ef2bc94059836a115430a6ad9d2838b0b34dc8f5
- https://git.kernel.org/stable/c/fcbacc47d16306c87ad1b820b7a575f6e9eae58b
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21981.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21981
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
