# [M] scsi: qla2xxx: Suppress a kernel complaint in qla_create_qpair()

## Summary
Severity: Medium
Advisory: CVE-2022-49155
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49155
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Suppress a kernel complaint in qla_create_qpair()

[   12.323788] BUG: using smp_processor_id() in preemptible [00000000] code: systemd-udevd/1020
[   12.332297] caller is qla2xxx_create_qpair+0x32a/0x5d0 [qla2xxx]
[   12.338417] CPU: 7 PID: 1020 Comm: systemd-udevd Tainted: G          I      --------- ---  5.14.0-29.el9.x86_64 #1
[   12.348827] Hardware name: Dell Inc. PowerEdge R610/0F0XJ6, BIOS 6.6.0 05/22/2018
[   12.356356] Call Trace:
[   12.358821]  dump_stack_lvl+0x34/0x44
[   12.362514]  check_preemption_disabled+0xd9/0xe0
[   12.367164]  qla2xxx_create_qpair+0x32a/0x5d0 [qla2xxx]
[   12.372481]  qla2x00_probe_one+0xa3a/0x1b80 [qla2xxx]
[   12.377617]  ? _raw_spin_lock_irqsave+0x19/0x40
[   12.384284]  local_pci_probe+0x42/0x80
[   12.390162]  ? pci_match_device+0xd7/0x110
[   12.396366]  pci_device_probe+0xfd/0x1b0
[   12.402372]  really_probe+0x1e7/0x3e0
[   12.408114]  __driver_probe_device+0xfe/0x180
[   12.414544]  driver_probe_device+0x1e/0x90
[   12.420685]  __driver_attach+0xc0/0x1c0
[   12.426536]  ? __device_attach_driver+0xe0/0xe0
[   12.433061]  ? __device_attach_driver+0xe0/0xe0
[   12.439538]  bus_for_each_dev+0x78/0xc0
[   12.445294]  bus_add_driver+0x12b/0x1e0
[   12.451021]  driver_register+0x8f/0xe0
[   12.456631]  ? 0xffffffffc07bc000
[   12.461773]  qla2x00_module_init+0x1be/0x229 [qla2xxx]
[   12.468776]  do_one_initcall+0x44/0x200
[   12.474401]  ? load_module+0xad3/0xba0
[   12.479908]  ? kmem_cache_alloc_trace+0x45/0x410
[   12.486268]  do_init_module+0x5c/0x280
[   12.491730]  __do_sys_init_module+0x12e/0x1b0
[   12.497785]  do_syscall_64+0x3b/0x90
[   12.503029]  entry_SYSCALL_64_after_hwframe+0x44/0xae
[   12.509764] RIP: 0033:0x7f554f73ab2e

## References
- https://git.kernel.org/stable/c/1ab81d82fb1db7ec4be4b0d04563513e6d4bcdd5
- https://git.kernel.org/stable/c/43195a0c620761fbb88db04e2475313855b948a4
- https://git.kernel.org/stable/c/8077a7162bc3cf658dd9ff112bc77716c08458c5
- https://git.kernel.org/stable/c/9c33d49ab9f3d8bd7512b3070cd2f07c4a8849d5
- https://git.kernel.org/stable/c/a60447e7d451df42c7bde43af53b34f10f34f469
- https://git.kernel.org/stable/c/a669a22aef0ceff706b885370af74b5a60a8ac85
- https://git.kernel.org/stable/c/f68776f28d9134fa65056e7e63bfc734049730b7
- https://git.kernel.org/stable/c/f97316dd393bc8df1cc2af6295a97b876eecf252
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49155.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49155
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
