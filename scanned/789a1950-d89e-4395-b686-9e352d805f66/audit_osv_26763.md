# [H] block/rq_qos: protect rq_qos apis with a new lock

## Summary
Severity: High
Advisory: CVE-2023-53823
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53823
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

block/rq_qos: protect rq_qos apis with a new lock

commit 50e34d78815e ("block: disable the elevator int del_gendisk")
move rq_qos_exit() from disk_release() to del_gendisk(), this will
introduce some problems:

1) If rq_qos_add() is triggered by enabling iocost/iolatency through
   cgroupfs, then it can concurrent with del_gendisk(), it's not safe to
   write 'q->rq_qos' concurrently.

2) Activate cgroup policy that is relied on rq_qos will call
   rq_qos_add() and blkcg_activate_policy(), and if rq_qos_exit() is
   called in the middle, null-ptr-dereference will be triggered in
   blkcg_activate_policy().

3) blkg_conf_open_bdev() can call blkdev_get_no_open() first to find the
   disk, then if rq_qos_exit() from del_gendisk() is done before
   rq_qos_add(), then memory will be leaked.

This patch add a new disk level mutex 'rq_qos_mutex':

1) The lock will protect rq_qos_exit() directly.

2) For wbt that doesn't relied on blk-cgroup, rq_qos_add() can only be
   called from disk initialization for now because wbt can't be
   destructed until rq_qos_exit(), so it's safe not to protect wbt for
   now. Hoever, in case that rq_qos dynamically destruction is supported
   in the furture, this patch also protect rq_qos_add() from wbt_init()
   directly, this is enough because blk-sysfs already synchronize
   writers with disk removal.

3) For iocost and iolatency, in order to synchronize disk removal and
   cgroup configuration, the lock is held after blkdev_get_no_open()
   from blkg_conf_open_bdev(), and is released in blkg_conf_exit().
   In order to fix the above memory leak, disk_live() is checked after
   holding the new lock.

## References
- https://git.kernel.org/stable/c/16398b4638b5cd8c1dc95fc940a1591a801d53ce
- https://git.kernel.org/stable/c/a13bd91be22318768d55470cbc0b0f4488ef9edf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53823.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53823
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
