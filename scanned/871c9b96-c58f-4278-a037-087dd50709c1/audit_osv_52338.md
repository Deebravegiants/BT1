# [M] CVE-2021-47344

## Summary
Severity: Medium
Advisory: CVE-2021-47344
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47344
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: zr364xx: fix memory leak in zr364xx_start_readpipe

syzbot reported memory leak in zr364xx driver.
The problem was in non-freed urb in case of
usb_submit_urb() fail.

backtrace:
  [<ffffffff82baedf6>] kmalloc include/linux/slab.h:561 [inline]
  [<ffffffff82baedf6>] usb_alloc_urb+0x66/0xe0 drivers/usb/core/urb.c:74
  [<ffffffff82f7cce8>] zr364xx_start_readpipe+0x78/0x130 drivers/media/usb/zr364xx/zr364xx.c:1022
  [<ffffffff84251dfc>] zr364xx_board_init drivers/media/usb/zr364xx/zr364xx.c:1383 [inline]
  [<ffffffff84251dfc>] zr364xx_probe+0x6a3/0x851 drivers/media/usb/zr364xx/zr364xx.c:1516
  [<ffffffff82bb6507>] usb_probe_interface+0x177/0x370 drivers/usb/core/driver.c:396
  [<ffffffff826018a9>] really_probe+0x159/0x500 drivers/base/dd.c:576

## References
- https://git.kernel.org/stable/c/021c294dff030f3ba38eb81e400ba123db32ecbc
- https://git.kernel.org/stable/c/0edd6759167295ea9969e89283b81017b4c688aa
- https://git.kernel.org/stable/c/b0633051a6cb24186ff04ce1af99c7de18c1987e
- https://git.kernel.org/stable/c/bbc80a972a3c5d7eba3f6c9c07af8fea42f5c513
- https://git.kernel.org/stable/c/c57b2bd3247925e253729dce283d6bf6abc9339d
- https://git.kernel.org/stable/c/c57bfd8000d7677bf435873b440eec0c47f73a08
- https://git.kernel.org/stable/c/0a045eac8d0427b64577a24d74bb8347c905ac65
- https://git.kernel.org/stable/c/5f3f81f1c96b501d180021c23c25e9f48eaab235
- https://git.kernel.org/stable/c/d69b39d89f362cfeeb54a68690768d0d257b2c8f
