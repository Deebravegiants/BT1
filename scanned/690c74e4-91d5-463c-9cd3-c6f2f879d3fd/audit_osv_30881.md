# [H] blk-cgroup: Fix UAF in blkcg_unpin_online()

## Summary
Severity: High
Advisory: CVE-2024-56672
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56672
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.121, >=6.2.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-cgroup: Fix UAF in blkcg_unpin_online()

blkcg_unpin_online() walks up the blkcg hierarchy putting the online pin. To
walk up, it uses blkcg_parent(blkcg) but it was calling that after
blkcg_destroy_blkgs(blkcg) which could free the blkcg, leading to the
following UAF:

  ==================================================================
  BUG: KASAN: slab-use-after-free in blkcg_unpin_online+0x15a/0x270
  Read of size 8 at addr ffff8881057678c0 by task kworker/9:1/117

  CPU: 9 UID: 0 PID: 117 Comm: kworker/9:1 Not tainted 6.13.0-rc1-work-00182-gb8f52214c61a-dirty #48
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS unknown 02/02/2022
  Workqueue: cgwb_release cgwb_release_workfn
  Call Trace:
   <TASK>
   dump_stack_lvl+0x27/0x80
   print_report+0x151/0x710
   kasan_report+0xc0/0x100
   blkcg_unpin_online+0x15a/0x270
   cgwb_release_workfn+0x194/0x480
   process_scheduled_works+0x71b/0xe20
   worker_thread+0x82a/0xbd0
   kthread+0x242/0x2c0
   ret_from_fork+0x33/0x70
   ret_from_fork_asm+0x1a/0x30
   </TASK>
  ...
  Freed by task 1944:
   kasan_save_track+0x2b/0x70
   kasan_save_free_info+0x3c/0x50
   __kasan_slab_free+0x33/0x50
   kfree+0x10c/0x330
   css_free_rwork_fn+0xe6/0xb30
   process_scheduled_works+0x71b/0xe20
   worker_thread+0x82a/0xbd0
   kthread+0x242/0x2c0
   ret_from_fork+0x33/0x70
   ret_from_fork_asm+0x1a/0x30

Note that the UAF is not easy to trigger as the free path is indirected
behind a couple RCU grace periods and a work item execution. I could only
trigger it with artifical msleep() injected in blkcg_unpin_online().

Fix it by reading the parent pointer before destroying the blkcg's blkg's.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/29d1e06560f0f6179062ac638b4064deb637d1ad
- https://git.kernel.org/stable/c/5baa28569c924d9a90d036c2aaab79f791fedaf8
- https://git.kernel.org/stable/c/64afc6fe24c9896c0153e5a199bcea241ecb0d5c
- https://git.kernel.org/stable/c/83f5a87ee8caa76a917f59912a74d6811f773c67
- https://git.kernel.org/stable/c/86e6ca55b83c575ab0f2e105cf08f98e58d3d7af
- https://git.kernel.org/stable/c/8a07350fe070017a887433f4d6909433955be5f1
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56672.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56672
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
