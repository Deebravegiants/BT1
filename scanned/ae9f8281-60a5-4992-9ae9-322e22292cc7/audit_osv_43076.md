# [H] md/raid5: avoid R5_Overlap races while breaking stripe batches

## Summary
Severity: High
Advisory: CVE-2026-72420
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72420
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid5: avoid R5_Overlap races while breaking stripe batches

KCSAN report a race in break_stripe_batch_list() vs. raid5_make_request()
on sh->dev[i].flags (plain word write vs. atomic bit op)..

and .. one possible scenario is:

CPU1                            CPU2
break_stripe_batch_list(sh1)
-> handle sh2
-> lock(sh2)
-> sh2->batch_head = NULL
-> unlock(sh2)
-> test_and_clear_bit(R5_Overlap, sh2->dev[i].flags)
-> wake_up_bit(sh2->dev[i].flags)
                                raid5_make_request()
                                -> add_all_stripe_bios(sh2)
                                -> lock(sh2)
                                -> stripe_bio_overlaps(sh2) returns true
				   batch_head is NULL, so new bio overlap
				   exist bio on sh2 -> true
                                -> set_bit(R5_Overlap, sh2->dev[i].flags)
                                -> unlock(sh2)
                                -> wait_on_bit(sh2->dev[i].flags)
-> sh2->dev[i].flags = sh1->dev[i].flags & ~R5_Overlap

No wait_up_bit(), CPU2 could be wait_on_bit() forever...

Fix by :
- Expand the protect zone.
- Use batch_head's device flag's snaphot when no held head_sh->stripe_lock.
- Move sh/head_sh->batch_head = NULL to the end of protected zone , and ,
  any concurrent add_all_stripe_bios() grabs sh->stripe_lock now either:
	- see batch_head != null, and , is rejected by stripe_bio_overlaps()
	  under the lock (no R5_Overlap wait ) , or ,
	- sees batch_head == NULL, only after dev[i].flags has already been
	  set and the prior R5_Overlap waiters worken.

KCSAN report:
================================================
  BUG: KCSAN: data-race in break_stripe_batch_list / raid5_make_request

  write (marked) to 0xffff8e89c8117548 of 8 bytes by task 4042 on cpu 0:
    raid5_make_request+0xea0/0x2930
    md_handle_request+0x4a2/0xa40
    md_submit_bio+0x109/0x1a0
    __submit_bio+0x2ec/0x390
    submit_bio_noacct_nocheck+0x457/0x710
    submit_bio_noacct+0x2a7/0xc20
    submit_bio+0x56/0x250
    blkdev_direct_IO+0x54c/0xda0
    blkdev_write_iter+0x38f/0x570
    aio_write+0x22b/0x490
    io_submit_one+0xa51/0xf70
    __x64_sys_io_submit+0xf7/0x220
    x64_sys_call+0x1907/0x1c60
    do_syscall_64+0x130/0x570
    entry_SYSCALL_64_after_hwframe+0x76/0x7e

  read to 0xffff8e89c8117548 of 8 bytes by task 4010 on cpu 5:
    break_stripe_batch_list+0x249/0x480
    handle_stripe_clean_event+0x720/0x9b0
    handle_stripe+0x32fb/0x4500
    handle_active_stripes.isra.0+0x6e0/0xa50
    raid5d+0x7e0/0xba0
    md_thread+0x15a/0x2d0
    kthread+0x1e3/0x220
    ret_from_fork+0x37a/0x410
    ret_from_fork_asm+0x1a/0x30

  value changed: 0x0000000000000019 -> 0x0000000000000099 --> R5_Overlap

## References
- https://git.kernel.org/stable/c/4d919c9b770996365806b6c8d701912d52baa306
- https://git.kernel.org/stable/c/55b77337bdd088c77461588e5ec094421b89911b
- https://git.kernel.org/stable/c/8031b0d02bd221a5f9add4357e291fc2a527b83a
- https://git.kernel.org/stable/c/d684b72dfbd320623ccaab0779aa841190488e7c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72420.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72420
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
