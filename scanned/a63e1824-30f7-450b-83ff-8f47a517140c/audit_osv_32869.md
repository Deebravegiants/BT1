# [H] binder: fix yet another UAF in binder_devices

## Summary
Severity: High
Advisory: CVE-2025-38175
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38175
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.14.11, >=6.15.0 <6.15.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: fix yet another UAF in binder_devices

Commit e77aff5528a18 ("binderfs: fix use-after-free in binder_devices")
addressed a use-after-free where devices could be released without first
being removed from the binder_devices list. However, there is a similar
path in binder_free_proc() that was missed:

  ==================================================================
  BUG: KASAN: slab-use-after-free in binder_remove_device+0xd4/0x100
  Write of size 8 at addr ffff0000c773b900 by task umount/467
  CPU: 12 UID: 0 PID: 467 Comm: umount Not tainted 6.15.0-rc7-00138-g57483a362741 #9 PREEMPT
  Hardware name: linux,dummy-virt (DT)
  Call trace:
   binder_remove_device+0xd4/0x100
   binderfs_evict_inode+0x230/0x2f0
   evict+0x25c/0x5dc
   iput+0x304/0x480
   dentry_unlink_inode+0x208/0x46c
   __dentry_kill+0x154/0x530
   [...]

  Allocated by task 463:
   __kmalloc_cache_noprof+0x13c/0x324
   binderfs_binder_device_create.isra.0+0x138/0xa60
   binder_ctl_ioctl+0x1ac/0x230
  [...]

  Freed by task 215:
   kfree+0x184/0x31c
   binder_proc_dec_tmpref+0x33c/0x4ac
   binder_deferred_func+0xc10/0x1108
   process_one_work+0x520/0xba4
  [...]
  ==================================================================

Call binder_remove_device() within binder_free_proc() to ensure the
device is removed from the binder_devices list before being kfreed.

## References
- https://git.kernel.org/stable/c/4a7694f499cae5b83412c5281bf2c961f34f2ed6
- https://git.kernel.org/stable/c/72a726fb5f25fbb31d6060acfb671c1955831245
- https://git.kernel.org/stable/c/9857af0fcff385c75433f2162c30c62eb912ef6d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38175.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38175
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
