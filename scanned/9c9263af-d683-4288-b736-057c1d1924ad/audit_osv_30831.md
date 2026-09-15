# [M] mm/gup: handle NULL pages in unpin_user_pages()

## Summary
Severity: Medium
Advisory: CVE-2024-56612
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56612
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/gup: handle NULL pages in unpin_user_pages()

The recent addition of "pofs" (pages or folios) handling to gup has a
flaw: it assumes that unpin_user_pages() handles NULL pages in the pages**
array.  That's not the case, as I discovered when I ran on a new
configuration on my test machine.

Fix this by skipping NULL pages in unpin_user_pages(), just like
unpin_folios() already does.

Details: when booting on x86 with "numa=fake=2 movablecore=4G" on Linux
6.12, and running this:

    tools/testing/selftests/mm/gup_longterm

...I get the following crash:

BUG: kernel NULL pointer dereference, address: 0000000000000008
RIP: 0010:sanity_check_pinned_pages+0x3a/0x2d0
...
Call Trace:
 <TASK>
 ? __die_body+0x66/0xb0
 ? page_fault_oops+0x30c/0x3b0
 ? do_user_addr_fault+0x6c3/0x720
 ? irqentry_enter+0x34/0x60
 ? exc_page_fault+0x68/0x100
 ? asm_exc_page_fault+0x22/0x30
 ? sanity_check_pinned_pages+0x3a/0x2d0
 unpin_user_pages+0x24/0xe0
 check_and_migrate_movable_pages_or_folios+0x455/0x4b0
 __gup_longterm_locked+0x3bf/0x820
 ? mmap_read_lock_killable+0x12/0x50
 ? __pfx_mmap_read_lock_killable+0x10/0x10
 pin_user_pages+0x66/0xa0
 gup_test_ioctl+0x358/0xb20
 __se_sys_ioctl+0x6b/0xc0
 do_syscall_64+0x7b/0x150
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

## References
- https://git.kernel.org/stable/c/69d319450d1c651f3b05cd820ff285fdd810c032
- https://git.kernel.org/stable/c/a1268be280d8e484ab3606d7476edd0f14bb9961
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56612.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56612
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
