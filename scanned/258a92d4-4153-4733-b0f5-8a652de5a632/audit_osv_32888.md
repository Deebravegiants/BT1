# [H] media: vivid: Change the siize of the composing

## Summary
Severity: High
Advisory: CVE-2025-38226
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38226
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.296, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.12.35, >=6.7.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: vivid: Change the siize of the composing

syzkaller found a bug:

BUG: KASAN: vmalloc-out-of-bounds in tpg_fill_plane_pattern drivers/media/common/v4l2-tpg/v4l2-tpg-core.c:2608 [inline]
BUG: KASAN: vmalloc-out-of-bounds in tpg_fill_plane_buffer+0x1a9c/0x5af0 drivers/media/common/v4l2-tpg/v4l2-tpg-core.c:2705
Write of size 1440 at addr ffffc9000d0ffda0 by task vivid-000-vid-c/5304

CPU: 0 UID: 0 PID: 5304 Comm: vivid-000-vid-c Not tainted 6.14.0-rc2-syzkaller-00039-g09fbf3d50205 #0
Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.3-debian-1.16.3-2~bpo12+1 04/01/2014

Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0x241/0x360 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:378 [inline]
 print_report+0x169/0x550 mm/kasan/report.c:489
 kasan_report+0x143/0x180 mm/kasan/report.c:602
 kasan_check_range+0x282/0x290 mm/kasan/generic.c:189
 __asan_memcpy+0x40/0x70 mm/kasan/shadow.c:106
 tpg_fill_plane_pattern drivers/media/common/v4l2-tpg/v4l2-tpg-core.c:2608 [inline]
 tpg_fill_plane_buffer+0x1a9c/0x5af0 drivers/media/common/v4l2-tpg/v4l2-tpg-core.c:2705
 vivid_fillbuff drivers/media/test-drivers/vivid/vivid-kthread-cap.c:470 [inline]
 vivid_thread_vid_cap_tick+0xf8e/0x60d0 drivers/media/test-drivers/vivid/vivid-kthread-cap.c:629
 vivid_thread_vid_cap+0x8aa/0xf30 drivers/media/test-drivers/vivid/vivid-kthread-cap.c:767
 kthread+0x7a9/0x920 kernel/kthread.c:464
 ret_from_fork+0x4b/0x80 arch/x86/kernel/process.c:148
 ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:244
 </TASK>

The composition size cannot be larger than the size of fmt_cap_rect.
So execute v4l2_rect_map_inside() even if has_compose_cap == 0.

## References
- https://git.kernel.org/stable/c/00da1c767a6567e56f23dda586847586868ac064
- https://git.kernel.org/stable/c/57597d8db5bbda618ba2145b7e8a7e6f01b6a27e
- https://git.kernel.org/stable/c/5d89aa42534723400fefd46e26e053b9c382b4ee
- https://git.kernel.org/stable/c/635cea4f44c1ddae208666772c164eab5a6bce39
- https://git.kernel.org/stable/c/89b5ab822bf69867c3951dd0eb34b0314c38966b
- https://git.kernel.org/stable/c/c56398885716d97ee9bcadb2bc9663a8c1757a34
- https://git.kernel.org/stable/c/f6b1b0f8ba0b61d8b511df5649d57235f230c135
- https://git.kernel.org/stable/c/f83ac8d30c43fd902af7c84c480f216157b60ef0
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38226.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38226
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
