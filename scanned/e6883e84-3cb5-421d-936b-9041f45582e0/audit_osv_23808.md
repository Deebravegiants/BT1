# [H] fbdev: defio: fix the pagelist corruption

## Summary
Severity: High
Advisory: CVE-2022-49511
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49511
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: defio: fix the pagelist corruption

Easily hit the below list corruption:
==
list_add corruption. prev->next should be next (ffffffffc0ceb090), but
was ffffec604507edc8. (prev=ffffec604507edc8).
WARNING: CPU: 65 PID: 3959 at lib/list_debug.c:26
__list_add_valid+0x53/0x80
CPU: 65 PID: 3959 Comm: fbdev Tainted: G     U
RIP: 0010:__list_add_valid+0x53/0x80
Call Trace:
 <TASK>
 fb_deferred_io_mkwrite+0xea/0x150
 do_page_mkwrite+0x57/0xc0
 do_wp_page+0x278/0x2f0
 __handle_mm_fault+0xdc2/0x1590
 handle_mm_fault+0xdd/0x2c0
 do_user_addr_fault+0x1d3/0x650
 exc_page_fault+0x77/0x180
 ? asm_exc_page_fault+0x8/0x30
 asm_exc_page_fault+0x1e/0x30
RIP: 0033:0x7fd98fc8fad1
==

Figure out the race happens when one process is adding &page->lru into
the pagelist tail in fb_deferred_io_mkwrite(), another process is
re-initializing the same &page->lru in fb_deferred_io_fault(), which is
not protected by the lock.

This fix is to init all the page lists one time during initialization,
it not only fixes the list corruption, but also avoids INIT_LIST_HEAD()
redundantly.

V2: change "int i" to "unsigned int i" (Geert Uytterhoeven)

## References
- https://git.kernel.org/stable/c/6a9ae2fe887042f76fd3d334349e64e8ab3c55a2
- https://git.kernel.org/stable/c/856082f021a28221db2c32bd0531614a8382be67
- https://git.kernel.org/stable/c/e79b2b2aadeffe1db54a6b569b9b621575c3eb07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49511.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49511
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
