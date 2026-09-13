# [H] iio: trigger: sysfs: fix use-after-free on remove

## Summary
Severity: High
Advisory: CVE-2022-49685
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49685
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.9.321, >=4.10.0 <4.14.286, >=4.15.0 <4.19.250, >=4.20.0 <5.4.202, >=5.5.0 <5.10.127, >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: trigger: sysfs: fix use-after-free on remove

Ensure that the irq_work has completed before the trigger is freed.

 ==================================================================
 BUG: KASAN: use-after-free in irq_work_run_list
 Read of size 8 at addr 0000000064702248 by task python3/25

 Call Trace:
  irq_work_run_list
  irq_work_tick
  update_process_times
  tick_sched_handle
  tick_sched_timer
  __hrtimer_run_queues
  hrtimer_interrupt

 Allocated by task 25:
  kmem_cache_alloc_trace
  iio_sysfs_trig_add
  dev_attr_store
  sysfs_kf_write
  kernfs_fop_write_iter
  new_sync_write
  vfs_write
  ksys_write
  sys_write

 Freed by task 25:
  kfree
  iio_sysfs_trig_remove
  dev_attr_store
  sysfs_kf_write
  kernfs_fop_write_iter
  new_sync_write
  vfs_write
  ksys_write
  sys_write

 ==================================================================

## References
- https://git.kernel.org/stable/c/31ff3309b47d98313c61b8301bf595820cc3cc33
- https://git.kernel.org/stable/c/4687c3f955240ca2a576bdc3f742d4d915b6272d
- https://git.kernel.org/stable/c/4ef1e521be610b720daeb7cf899fedc7db0274c4
- https://git.kernel.org/stable/c/5e39397d60dacc7f5d81d442c1c958eaaaf31128
- https://git.kernel.org/stable/c/78601726d4a59a291acc5a52da1d3a0a6831e4e8
- https://git.kernel.org/stable/c/b07a30a774b3c3e584a68dc91779c68ea2da4813
- https://git.kernel.org/stable/c/d6111e7bdb8ec27eb43d01c4cd4ff1620a75f7f2
- https://git.kernel.org/stable/c/fd5d8fb298a2866c337da635c79d63c3afabcaf7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49685.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49685
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
