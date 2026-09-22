# [H] drm/amd/display: Check NULL before accessing

## Summary
Severity: High
Advisory: CVE-2025-68286
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68286
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.119, >=6.7.0 <6.12.61, >=6.13.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Check NULL before accessing

[WHAT]
IGT kms_cursor_legacy's long-nonblocking-modeset-vs-cursor-atomic
fails with NULL pointer dereference. This can be reproduced with
both an eDP panel and a DP monitors connected.

 BUG: kernel NULL pointer dereference, address: 0000000000000000
 #PF: supervisor read access in kernel mode
 #PF: error_code(0x0000) - not-present page
 PGD 0 P4D 0
 Oops: Oops: 0000 [#1] SMP NOPTI
 CPU: 13 UID: 0 PID: 2960 Comm: kms_cursor_lega Not tainted
6.16.0-99-custom #8 PREEMPT(voluntary)
 Hardware name: AMD ........
 RIP: 0010:dc_stream_get_scanoutpos+0x34/0x130 [amdgpu]
 Code: 57 4d 89 c7 41 56 49 89 ce 41 55 49 89 d5 41 54 49
 89 fc 53 48 83 ec 18 48 8b 87 a0 64 00 00 48 89 75 d0 48 c7 c6 e0 41 30
 c2 <48> 8b 38 48 8b 9f 68 06 00 00 e8 8d d7 fd ff 31 c0 48 81 c3 e0 02
 RSP: 0018:ffffd0f3c2bd7608 EFLAGS: 00010292
 RAX: 0000000000000000 RBX: 0000000000000000 RCX: ffffd0f3c2bd7668
 RDX: ffffd0f3c2bd7664 RSI: ffffffffc23041e0 RDI: ffff8b32494b8000
 RBP: ffffd0f3c2bd7648 R08: ffffd0f3c2bd766c R09: ffffd0f3c2bd7760
 R10: ffffd0f3c2bd7820 R11: 0000000000000000 R12: ffff8b32494b8000
 R13: ffffd0f3c2bd7664 R14: ffffd0f3c2bd7668 R15: ffffd0f3c2bd766c
 FS:  000071f631b68700(0000) GS:ffff8b399f114000(0000)
knlGS:0000000000000000
 CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
 CR2: 0000000000000000 CR3: 00000001b8105000 CR4: 0000000000f50ef0
 PKRU: 55555554
 Call Trace:
 <TASK>
 dm_crtc_get_scanoutpos+0xd7/0x180 [amdgpu]
 amdgpu_display_get_crtc_scanoutpos+0x86/0x1c0 [amdgpu]
 ? __pfx_amdgpu_crtc_get_scanout_position+0x10/0x10[amdgpu]
 amdgpu_crtc_get_scanout_position+0x27/0x50 [amdgpu]
 drm_crtc_vblank_helper_get_vblank_timestamp_internal+0xf7/0x400
 drm_crtc_vblank_helper_get_vblank_timestamp+0x1c/0x30
 drm_crtc_get_last_vbltimestamp+0x55/0x90
 drm_crtc_next_vblank_start+0x45/0xa0
 drm_atomic_helper_wait_for_fences+0x81/0x1f0
 ...

(cherry picked from commit 621e55f1919640acab25383362b96e65f2baea3c)

## References
- https://git.kernel.org/stable/c/09092269cb762378ca8b56024746b1a136761e0d
- https://git.kernel.org/stable/c/109e9c92543f3105e8e1efd2c5e6b92ef55d5743
- https://git.kernel.org/stable/c/3ce62c189693e8ed7b3abe551802bbc67f3ace54
- https://git.kernel.org/stable/c/62150f1e7ec707da76ff353fb7db51fef9cd6557
- https://git.kernel.org/stable/c/781f2f32e9c19eb791b52af283c96f9a9677a7f2
- https://git.kernel.org/stable/c/9d1a65cbe3ec5da3003c8434ac7a38dcdc958fd9
- https://git.kernel.org/stable/c/f7cf491cd5b54b5a093bd3fdf76fa2860a7522bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68286.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68286
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
