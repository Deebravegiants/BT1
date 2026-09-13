# [H] f2fs: compress: fix to call f2fs_wait_on_page_writeback() in f2fs_write_raw_pages()

## Summary
Severity: High
Advisory: CVE-2023-54068
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54068
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: compress: fix to call f2fs_wait_on_page_writeback() in f2fs_write_raw_pages()

BUG_ON() will be triggered when writing files concurrently,
because the same page is writtenback multiple times.

1597 void folio_end_writeback(struct folio *folio)
1598 {
		......
1618     if (!__folio_end_writeback(folio))
1619         BUG();
		......
1625 }

kernel BUG at mm/filemap.c:1619!
Call Trace:
 <TASK>
 f2fs_write_end_io+0x1a0/0x370
 blk_update_request+0x6c/0x410
 blk_mq_end_request+0x15/0x130
 blk_complete_reqs+0x3c/0x50
 __do_softirq+0xb8/0x29b
 ? sort_range+0x20/0x20
 run_ksoftirqd+0x19/0x20
 smpboot_thread_fn+0x10b/0x1d0
 kthread+0xde/0x110
 ? kthread_complete_and_exit+0x20/0x20
 ret_from_fork+0x22/0x30
 </TASK>

Below is the concurrency scenario:

[Process A]		[Process B]		[Process C]
f2fs_write_raw_pages()
  - redirty_page_for_writepage()
  - unlock page()
			f2fs_do_write_data_page()
			  - lock_page()
			  - clear_page_dirty_for_io()
			  - set_page_writeback() [1st writeback]
			    .....
			    - unlock page()

						generic_perform_write()
						  - f2fs_write_begin()
						    - wait_for_stable_page()

						  - f2fs_write_end()
						    - set_page_dirty()

  - lock_page()
    - f2fs_do_write_data_page()
      - set_page_writeback() [2st writeback]

This problem was introduced by the previous commit 7377e853967b ("f2fs:
compress: fix potential deadlock of compress file"). All pagelocks were
released in f2fs_write_raw_pages(), but whether the page was
in the writeback state was ignored in the subsequent writing process.
Let's fix it by waiting for the page to writeback before writing.

## References
- https://git.kernel.org/stable/c/169134da419cb8ffbe3b0743bc24573e16952ea9
- https://git.kernel.org/stable/c/6604df2a9d07ba8f8fb1ac14046c2c83776faa4f
- https://git.kernel.org/stable/c/9940877c4fe752923a53f0f7372f2f152b6eccf0
- https://git.kernel.org/stable/c/a8226a45b2a9ce83ba7a167a387a00fecc319e71
- https://git.kernel.org/stable/c/ad31eed06c3b4d63b2d38322a271d4009aee4bb3
- https://git.kernel.org/stable/c/babedcbac164cec970872b8097401ca913a80e61
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54068.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54068
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
