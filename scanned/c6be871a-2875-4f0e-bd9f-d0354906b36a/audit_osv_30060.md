# [H] fbdev: pxafb: Fix possible use after free in pxafb_task()

## Summary
Severity: High
Advisory: CVE-2024-49924
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49924
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: pxafb: Fix possible use after free in pxafb_task()

In the pxafb_probe function, it calls the pxafb_init_fbinfo function,
after which &fbi->task is associated with pxafb_task. Moreover,
within this pxafb_init_fbinfo function, the pxafb_blank function
within the &pxafb_ops struct is capable of scheduling work.

If we remove the module which will call pxafb_remove to make cleanup,
it will call unregister_framebuffer function which can call
do_unregister_framebuffer to free fbi->fb through
put_fb_info(fb_info), while the work mentioned above will be used.
The sequence of operations that may lead to a UAF bug is as follows:

CPU0                                                CPU1

                                   | pxafb_task
pxafb_remove                       |
unregister_framebuffer(info)       |
do_unregister_framebuffer(fb_info) |
put_fb_info(fb_info)               |
// free fbi->fb                    | set_ctrlr_state(fbi, state)
                                   | __pxafb_lcd_power(fbi, 0)
                                   | fbi->lcd_power(on, &fbi->fb.var)
                                   | //use fbi->fb

Fix it by ensuring that the work is canceled before proceeding
with the cleanup in pxafb_remove.

Note that only root user can remove the driver at runtime.

## References
- https://git.kernel.org/stable/c/3c0d416eb4bef705f699213cee94bf54b6acdacd
- https://git.kernel.org/stable/c/4a6921095eb04a900e0000da83d9475eb958e61e
- https://git.kernel.org/stable/c/4cda484e584be34d55ee17436ebf7ad11922b97a
- https://git.kernel.org/stable/c/6d0a07f68b66269e167def6c0b90a219cd3e7473
- https://git.kernel.org/stable/c/a3a855764dbacbdb1cc51e15dc588f2d21c93e0e
- https://git.kernel.org/stable/c/aaadc0cb05c999ccd8898a03298b7e5c31509b08
- https://git.kernel.org/stable/c/e657fa2df4429f3805a9b3e47fb1a4a1b02a72bd
- https://git.kernel.org/stable/c/e6897e299f57b103e999e62010b88e363b3eebae
- https://git.kernel.org/stable/c/fdda354f60a576d52dcf90351254714681df4370
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49924.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49924
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
