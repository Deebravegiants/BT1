# [M] net/mlx5: Unregister notifier on eswitch init failure

## Summary
Severity: Medium
Advisory: CVE-2024-50136
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50136
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.115, >=6.2.0 <6.6.59, >=6.6.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Unregister notifier on eswitch init failure

It otherwise remains registered and a subsequent attempt at eswitch
enabling might trigger warnings of the sort:

[  682.589148] ------------[ cut here ]------------
[  682.590204] notifier callback eswitch_vport_event [mlx5_core] already registered
[  682.590256] WARNING: CPU: 13 PID: 2660 at kernel/notifier.c:31 notifier_chain_register+0x3e/0x90
[...snipped]
[  682.610052] Call Trace:
[  682.610369]  <TASK>
[  682.610663]  ? __warn+0x7c/0x110
[  682.611050]  ? notifier_chain_register+0x3e/0x90
[  682.611556]  ? report_bug+0x148/0x170
[  682.611977]  ? handle_bug+0x36/0x70
[  682.612384]  ? exc_invalid_op+0x13/0x60
[  682.612817]  ? asm_exc_invalid_op+0x16/0x20
[  682.613284]  ? notifier_chain_register+0x3e/0x90
[  682.613789]  atomic_notifier_chain_register+0x25/0x40
[  682.614322]  mlx5_eswitch_enable_locked+0x1d4/0x3b0 [mlx5_core]
[  682.614965]  mlx5_eswitch_enable+0xc9/0x100 [mlx5_core]
[  682.615551]  mlx5_device_enable_sriov+0x25/0x340 [mlx5_core]
[  682.616170]  mlx5_core_sriov_configure+0x50/0x170 [mlx5_core]
[  682.616789]  sriov_numvfs_store+0xb0/0x1b0
[  682.617248]  kernfs_fop_write_iter+0x117/0x1a0
[  682.617734]  vfs_write+0x231/0x3f0
[  682.618138]  ksys_write+0x63/0xe0
[  682.618536]  do_syscall_64+0x4c/0x100
[  682.618958]  entry_SYSCALL_64_after_hwframe+0x4b/0x53

## References
- https://git.kernel.org/stable/c/1da9cfd6c41c2e6bbe624d0568644e1521c33e12
- https://git.kernel.org/stable/c/599147722c5778c96292e2fbff4103abbdb45b1f
- https://git.kernel.org/stable/c/9f2ccb6f3888bec45c00121ee43e4e72423b12c1
- https://git.kernel.org/stable/c/e58fb7ddbab6635191c26dea1af26b91cce00866
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50136.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50136
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
