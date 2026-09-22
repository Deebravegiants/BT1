# [H] RDMA/srpt: Fix a use-after-free

## Summary
Severity: High
Advisory: CVE-2022-50129
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50129
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/srpt: Fix a use-after-free

Change the LIO port members inside struct srpt_port from regular members
into pointers. Allocate the LIO port data structures from inside
srpt_make_tport() and free these from inside srpt_make_tport(). Keep
struct srpt_device as long as either an RDMA port or a LIO target port is
associated with it. This patch decouples the lifetime of struct srpt_port
(controlled by the RDMA core) and struct srpt_port_id (controlled by LIO).
This patch fixes the following KASAN complaint:

  BUG: KASAN: use-after-free in srpt_enable_tpg+0x31/0x70 [ib_srpt]
  Read of size 8 at addr ffff888141cc34b8 by task check/5093

  Call Trace:
   <TASK>
   show_stack+0x4e/0x53
   dump_stack_lvl+0x51/0x66
   print_address_description.constprop.0.cold+0xea/0x41e
   print_report.cold+0x90/0x205
   kasan_report+0xb9/0xf0
   __asan_load8+0x69/0x90
   srpt_enable_tpg+0x31/0x70 [ib_srpt]
   target_fabric_tpg_base_enable_store+0xe2/0x140 [target_core_mod]
   configfs_write_iter+0x18b/0x210
   new_sync_write+0x1f2/0x2f0
   vfs_write+0x3e3/0x540
   ksys_write+0xbb/0x140
   __x64_sys_write+0x42/0x50
   do_syscall_64+0x34/0x80
   entry_SYSCALL_64_after_hwframe+0x46/0xb0
   </TASK>

## References
- https://git.kernel.org/stable/c/388326bb1c32fcd09371c1d494af71471ef3a04b
- https://git.kernel.org/stable/c/4ee8c39968a648d58b273582d4b021044a41ee5e
- https://git.kernel.org/stable/c/b5605148e6ce36bb21020d49010b617693933128
- https://git.kernel.org/stable/c/de95b52d9aabc979166aba81ccbe623aaf9c16a1
- https://git.kernel.org/stable/c/e60d7e2462bf57273563c4e00dbfa79ee973b9e2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50129.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50129
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
