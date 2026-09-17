# [H] drm/atmel-hlcdc: fix use-after-free of drm_crtc_commit after release

## Summary
Severity: High
Advisory: CVE-2026-43236
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43236
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/atmel-hlcdc: fix use-after-free of drm_crtc_commit after release

The atmel_hlcdc_plane_atomic_duplicate_state() callback was copying
the atmel_hlcdc_plane state structure without properly duplicating the
drm_plane_state. In particular, state->commit remained set to the old
state commit, which can lead to a use-after-free in the next
drm_atomic_commit() call.

Fix this by calling
__drm_atomic_helper_duplicate_plane_state(), which correctly clones
the base drm_plane_state (including the ->commit pointer).

It has been seen when closing and re-opening the device node while
another DRM client (e.g. fbdev) is still attached:

=============================================================================
BUG kmalloc-64 (Not tainted): Poison overwritten
-----------------------------------------------------------------------------

0xc611b344-0xc611b344 @offset=836. First byte 0x6a instead of 0x6b
FIX kmalloc-64: Restoring Poison 0xc611b344-0xc611b344=0x6b
Allocated in drm_atomic_helper_setup_commit+0x1e8/0x7bc age=178 cpu=0
pid=29
 drm_atomic_helper_setup_commit+0x1e8/0x7bc
 drm_atomic_helper_commit+0x3c/0x15c
 drm_atomic_commit+0xc0/0xf4
 drm_framebuffer_remove+0x4cc/0x5a8
 drm_mode_rmfb_work_fn+0x6c/0x80
 process_one_work+0x12c/0x2cc
 worker_thread+0x2a8/0x400
 kthread+0xc0/0xdc
 ret_from_fork+0x14/0x28
Freed in drm_atomic_helper_commit_hw_done+0x100/0x150 age=8 cpu=0
pid=169
 drm_atomic_helper_commit_hw_done+0x100/0x150
 drm_atomic_helper_commit_tail+0x64/0x8c
 commit_tail+0x168/0x18c
 drm_atomic_helper_commit+0x138/0x15c
 drm_atomic_commit+0xc0/0xf4
 drm_atomic_helper_set_config+0x84/0xb8
 drm_mode_setcrtc+0x32c/0x810
 drm_ioctl+0x20c/0x488
 sys_ioctl+0x14c/0xc20
 ret_fast_syscall+0x0/0x54
Slab 0xef8bc360 objects=21 used=16 fp=0xc611b7c0
flags=0x200(workingset|zone=0)
Object 0xc611b340 @offset=832 fp=0xc611b7c0

## References
- https://git.kernel.org/stable/c/549c6db503dbb85dbff4840830971853feac6625
- https://git.kernel.org/stable/c/6404898af86d986db1dbbe06177c143e40652e49
- https://git.kernel.org/stable/c/796e77c14c4c1e2cd36473760fb6cc66c695eb47
- https://git.kernel.org/stable/c/7b4d0fab3ff2c00c6d34e1952c9df5129a826aee
- https://git.kernel.org/stable/c/a205740a7231e967ac77cb731171642901c327af
- https://git.kernel.org/stable/c/ac2d898da5095d46bd1ff8585fdd753d58ad91e7
- https://git.kernel.org/stable/c/bc847787233277a337788568e90a6ee1557595eb
- https://git.kernel.org/stable/c/fd4a4d0711f48a99b25bcd45e00eef8339eff82d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43236.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43236
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
