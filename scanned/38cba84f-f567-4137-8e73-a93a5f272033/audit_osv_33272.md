# [H] net/mlx5: fs, fix UAF in flow counter release

## Summary
Severity: High
Advisory: CVE-2025-39979
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39979
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: fs, fix UAF in flow counter release

Fix a kernel trace [1] caused by releasing an HWS action of a local flow
counter in mlx5_cmd_hws_delete_fte(), where the HWS action refcount and
mutex were not initialized and the counter struct could already be freed
when deleting the rule.

Fix it by adding the missing initializations and adding refcount for the
local flow counter struct.

[1] Kernel log:
 Call Trace:
  <TASK>
  dump_stack_lvl+0x34/0x48
  mlx5_fs_put_hws_action.part.0.cold+0x21/0x94 [mlx5_core]
  mlx5_fc_put_hws_action+0x96/0xad [mlx5_core]
  mlx5_fs_destroy_fs_actions+0x8b/0x152 [mlx5_core]
  mlx5_cmd_hws_delete_fte+0x5a/0xa0 [mlx5_core]
  del_hw_fte+0x1ce/0x260 [mlx5_core]
  mlx5_del_flow_rules+0x12d/0x240 [mlx5_core]
  ? ttwu_queue_wakelist+0xf4/0x110
  mlx5_ib_destroy_flow+0x103/0x1b0 [mlx5_ib]
  uverbs_free_flow+0x20/0x50 [ib_uverbs]
  destroy_hw_idr_uobject+0x1b/0x50 [ib_uverbs]
  uverbs_destroy_uobject+0x34/0x1a0 [ib_uverbs]
  uobj_destroy+0x3c/0x80 [ib_uverbs]
  ib_uverbs_run_method+0x23e/0x360 [ib_uverbs]
  ? uverbs_finalize_object+0x60/0x60 [ib_uverbs]
  ib_uverbs_cmd_verbs+0x14f/0x2c0 [ib_uverbs]
  ? do_tty_write+0x1a9/0x270
  ? file_tty_write.constprop.0+0x98/0xc0
  ? new_sync_write+0xfc/0x190
  ib_uverbs_ioctl+0xd7/0x160 [ib_uverbs]
  __x64_sys_ioctl+0x87/0xc0
  do_syscall_64+0x59/0x90

## References
- https://git.kernel.org/stable/c/3c77f6d244188c3fb11f6aec40bbfe884f1803b5
- https://git.kernel.org/stable/c/6043819e707cefb1c9e59d6e431dcfa735c4f975
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39979.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39979
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
