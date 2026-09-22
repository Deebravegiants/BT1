# [M] CVE-2021-47375

## Summary
Severity: Medium
Advisory: CVE-2021-47375
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47375
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

blktrace: Fix uaf in blk_trace access after removing by sysfs

There is an use-after-free problem triggered by following process:

      P1(sda)				P2(sdb)
			echo 0 > /sys/block/sdb/trace/enable
			  blk_trace_remove_queue
			    synchronize_rcu
			    blk_trace_free
			      relay_close
rcu_read_lock
__blk_add_trace
  trace_note_tsk
  (Iterate running_trace_list)
			        relay_close_buf
				  relay_destroy_buf
				    kfree(buf)
    trace_note(sdb's bt)
      relay_reserve
        buf->offset <- nullptr deference (use-after-free) !!!
rcu_read_unlock

[  502.714379] BUG: kernel NULL pointer dereference, address:
0000000000000010
[  502.715260] #PF: supervisor read access in kernel mode
[  502.715903] #PF: error_code(0x0000) - not-present page
[  502.716546] PGD 103984067 P4D 103984067 PUD 17592b067 PMD 0
[  502.717252] Oops: 0000 [#1] SMP
[  502.720308] RIP: 0010:trace_note.isra.0+0x86/0x360
[  502.732872] Call Trace:
[  502.733193]  __blk_add_trace.cold+0x137/0x1a3
[  502.733734]  blk_add_trace_rq+0x7b/0xd0
[  502.734207]  blk_add_trace_rq_issue+0x54/0xa0
[  502.734755]  blk_mq_start_request+0xde/0x1b0
[  502.735287]  scsi_queue_rq+0x528/0x1140
...
[  502.742704]  sg_new_write.isra.0+0x16e/0x3e0
[  502.747501]  sg_ioctl+0x466/0x1100

Reproduce method:
  ioctl(/dev/sda, BLKTRACESETUP, blk_user_trace_setup[buf_size=127])
  ioctl(/dev/sda, BLKTRACESTART)
  ioctl(/dev/sdb, BLKTRACESETUP, blk_user_trace_setup[buf_size=127])
  ioctl(/dev/sdb, BLKTRACESTART)

  echo 0 > /sys/block/sdb/trace/enable &
  // Add delay(mdelay/msleep) before kernel enters blk_trace_free()

  ioctl$SG_IO(/dev/sda, SG_IO, ...)
  // Enters trace_note_tsk() after blk_trace_free() returned
  // Use mdelay in rcu region rather than msleep(which may schedule out)

Remove blk_trace from running_list before calling blk_trace_free() by
sysfs if blk_trace is at Blktrace_running state.

## References
- https://git.kernel.org/stable/c/3815fe7371d2411ce164281cef40d9fc7b323dee
- https://git.kernel.org/stable/c/488da313edf3abea7f7733efe011c96b23740ab5
- https://git.kernel.org/stable/c/5afedf670caf30a2b5a52da96eb7eac7dee6a9c9
- https://git.kernel.org/stable/c/677e362ba807f3aafe6f405c07e0b37244da5222
- https://git.kernel.org/stable/c/a5f8e86192612d0183047448d8bbe7918b3f1a26
- https://git.kernel.org/stable/c/d56171d9360c0170c5c5f8f7e2362a2e999eca40
- https://git.kernel.org/stable/c/dacfd5e4d1142bfb3809aab3634a375f6f373269
- https://git.kernel.org/stable/c/ebb8d26d93c3ec3c7576c52a8373a2309423c069
