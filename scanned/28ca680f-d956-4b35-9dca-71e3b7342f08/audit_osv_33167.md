# [M] net/mlx5: Fix lockdep assertion on sync reset unload event

## Summary
Severity: Medium
Advisory: CVE-2025-39832
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39832
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.104, >=6.7.0 <6.12.45, >=6.13.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Fix lockdep assertion on sync reset unload event

Fix lockdep assertion triggered during sync reset unload event. When the
sync reset flow is initiated using the devlink reload fw_activate
option, the PF already holds the devlink lock while handling unload
event. In this case, delegate sync reset unload event handling back to
the devlink callback process to avoid double-locking and resolve the
lockdep warning.

Kernel log:
WARNING: CPU: 9 PID: 1578 at devl_assert_locked+0x31/0x40
[...]
Call Trace:
<TASK>
 mlx5_unload_one_devl_locked+0x2c/0xc0 [mlx5_core]
 mlx5_sync_reset_unload_event+0xaf/0x2f0 [mlx5_core]
 process_one_work+0x222/0x640
 worker_thread+0x199/0x350
 kthread+0x10b/0x230
 ? __pfx_worker_thread+0x10/0x10
 ? __pfx_kthread+0x10/0x10
 ret_from_fork+0x8e/0x100
 ? __pfx_kthread+0x10/0x10
 ret_from_fork_asm+0x1a/0x30
</TASK>

## References
- https://git.kernel.org/stable/c/06d897148e79638651800d851a69547b56b4be2e
- https://git.kernel.org/stable/c/0c87dba9ccd3801d3b503f0b4fd41be343af4f06
- https://git.kernel.org/stable/c/902a8bc23a24882200f57cadc270e15a2cfaf2bb
- https://git.kernel.org/stable/c/ddac9d0fe2493dd550cbfc75eeaf31e9b6dac959
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39832.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39832
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
