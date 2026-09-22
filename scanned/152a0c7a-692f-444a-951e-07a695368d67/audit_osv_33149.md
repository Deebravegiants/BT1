# [M] drm/mediatek: Add error handling for old state CRTC in atomic_disable

## Summary
Severity: Medium
Advisory: CVE-2025-39807
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39807
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.45, >=6.13.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/mediatek: Add error handling for old state CRTC in atomic_disable

Introduce error handling to address an issue where, after a hotplug
event, the cursor continues to update. This situation can lead to a
kernel panic due to accessing the NULL `old_state->crtc`.

E,g.
Unable to handle kernel NULL pointer dereference at virtual address
Call trace:
 mtk_crtc_plane_disable+0x24/0x140
 mtk_plane_atomic_update+0x8c/0xa8
 drm_atomic_helper_commit_planes+0x114/0x2c8
 drm_atomic_helper_commit_tail_rpm+0x4c/0x158
 commit_tail+0xa0/0x168
 drm_atomic_helper_commit+0x110/0x120
 drm_atomic_commit+0x8c/0xe0
 drm_atomic_helper_update_plane+0xd4/0x128
 __setplane_atomic+0xcc/0x110
 drm_mode_cursor_common+0x250/0x440
 drm_mode_cursor_ioctl+0x44/0x70
 drm_ioctl+0x264/0x5d8
 __arm64_sys_ioctl+0xd8/0x510
 invoke_syscall+0x6c/0xe0
 do_el0_svc+0x68/0xe8
 el0_svc+0x34/0x60
 el0t_64_sync_handler+0x1c/0xf8
 el0t_64_sync+0x180/0x188

Adding NULL pointer checks to ensure stability by preventing operations
on an invalid CRTC state.

## References
- https://git.kernel.org/stable/c/0c6b24d70da21201ed009a2aca740d2dfddc7ab5
- https://git.kernel.org/stable/c/7d5cc22efa44e0fe321ce195c71c3d7da211fbb2
- https://git.kernel.org/stable/c/9a94e9d8b50bcfe89693bc899a54d3866d86e973
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39807.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39807
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
