# [H] CVE-2021-47383

## Summary
Severity: High
Advisory: CVE-2021-47383
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47383
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

tty: Fix out-of-bound vmalloc access in imageblit

This issue happens when a userspace program does an ioctl
FBIOPUT_VSCREENINFO passing the fb_var_screeninfo struct
containing only the fields xres, yres, and bits_per_pixel
with values.

If this struct is the same as the previous ioctl, the
vc_resize() detects it and doesn't call the resize_screen(),
leaving the fb_var_screeninfo incomplete. And this leads to
the updatescrollmode() calculates a wrong value to
fbcon_display->vrows, which makes the real_y() return a
wrong value of y, and that value, eventually, causes
the imageblit to access an out-of-bound address value.

To solve this issue I made the resize_screen() be called
even if the screen does not need any resizing, so it will
"fix and fill" the fb_var_screeninfo independently.

## References
- https://git.kernel.org/stable/c/70aed03b1d5a5df974f456cdc8eedb213c94bb8b
- https://git.kernel.org/stable/c/7e71fcedfda6f7de18f850a6b36e78d78b04476f
- https://git.kernel.org/stable/c/883f7897a25e3ce14a7f274ca4c73f49ac84002a
- https://git.kernel.org/stable/c/8a6a240f52e14356386030d8958ae8b1761d2325
- https://git.kernel.org/stable/c/d570c48dd37dbe8fc6875d4461d01a9554ae2560
- https://git.kernel.org/stable/c/067c694d06040db6f0c65281bb358452ca6d85b9
- https://git.kernel.org/stable/c/3b0c406124719b625b1aba431659f5cdc24a982c
- https://git.kernel.org/stable/c/699d926585daa6ec44be556cdc1ab89e5d54557b
