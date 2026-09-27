# [H] net/mlx5e: CT: Fix null-ptr-deref in add rule err flow

## Summary
Severity: High
Advisory: CVE-2024-53120
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53120
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.174, >=5.16.0 <6.1.119, >=6.2.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: CT: Fix null-ptr-deref in add rule err flow

In error flow of mlx5_tc_ct_entry_add_rule(), in case ct_rule_add()
callback returns error, zone_rule->attr is used uninitiated. Fix it to
use attr which has the needed pointer value.

Kernel log:
 BUG: kernel NULL pointer dereference, address: 0000000000000110
 RIP: 0010:mlx5_tc_ct_entry_add_rule+0x2b1/0x2f0 [mlx5_core]
…
 Call Trace:
  <TASK>
  ? __die+0x20/0x70
  ? page_fault_oops+0x150/0x3e0
  ? exc_page_fault+0x74/0x140
  ? asm_exc_page_fault+0x22/0x30
  ? mlx5_tc_ct_entry_add_rule+0x2b1/0x2f0 [mlx5_core]
  ? mlx5_tc_ct_entry_add_rule+0x1d5/0x2f0 [mlx5_core]
  mlx5_tc_ct_block_flow_offload+0xc6a/0xf90 [mlx5_core]
  ? nf_flow_offload_tuple+0xd8/0x190 [nf_flow_table]
  nf_flow_offload_tuple+0xd8/0x190 [nf_flow_table]
  flow_offload_work_handler+0x142/0x320 [nf_flow_table]
  ? finish_task_switch.isra.0+0x15b/0x2b0
  process_one_work+0x16c/0x320
  worker_thread+0x28c/0x3a0
  ? __pfx_worker_thread+0x10/0x10
  kthread+0xb8/0xf0
  ? __pfx_kthread+0x10/0x10
  ret_from_fork+0x2d/0x50
  ? __pfx_kthread+0x10/0x10
  ret_from_fork_asm+0x1a/0x30
  </TASK>

## References
- https://git.kernel.org/stable/c/06dc488a593020bd2f006798557d2a32104d8359
- https://git.kernel.org/stable/c/0c7c70ff8b696cfedba350411dca736361ef9a0f
- https://git.kernel.org/stable/c/6030f8bd7902e9e276a0edc09bf11979e4e2bc2e
- https://git.kernel.org/stable/c/882f392d9e3649557e71efd78ae20c86039ffb7c
- https://git.kernel.org/stable/c/e99c6873229fe0482e7ceb7d5600e32d623ed9d9
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53120.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53120
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
