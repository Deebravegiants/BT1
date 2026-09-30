# [H] cnic: Fix use-after-free bugs in cnic_delete_task

## Summary
Severity: High
Advisory: CVE-2025-39945
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39945
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <5.4.300, >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.154, >=6.2.0 <6.6.108, >=6.7.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

cnic: Fix use-after-free bugs in cnic_delete_task

The original code uses cancel_delayed_work() in cnic_cm_stop_bnx2x_hw(),
which does not guarantee that the delayed work item 'delete_task' has
fully completed if it was already running. Additionally, the delayed work
item is cyclic, the flush_workqueue() in cnic_cm_stop_bnx2x_hw() only
blocks and waits for work items that were already queued to the
workqueue prior to its invocation. Any work items submitted after
flush_workqueue() is called are not included in the set of tasks that the
flush operation awaits. This means that after the cyclic work items have
finished executing, a delayed work item may still exist in the workqueue.
This leads to use-after-free scenarios where the cnic_dev is deallocated
by cnic_free_dev(), while delete_task remains active and attempt to
dereference cnic_dev in cnic_delete_task().

A typical race condition is illustrated below:

CPU 0 (cleanup)              | CPU 1 (delayed work callback)
cnic_netdev_event()          |
  cnic_stop_hw()             | cnic_delete_task()
    cnic_cm_stop_bnx2x_hw()  | ...
      cancel_delayed_work()  | /* the queue_delayed_work()
      flush_workqueue()      |    executes after flush_workqueue()*/
                             | queue_delayed_work()
  cnic_free_dev(dev)//free   | cnic_delete_task() //new instance
                             |   dev = cp->dev; //use

Replace cancel_delayed_work() with cancel_delayed_work_sync() to ensure
that the cyclic delayed work item is properly canceled and that any
ongoing execution of the work item completes before the cnic_dev is
deallocated. Furthermore, since cancel_delayed_work_sync() uses
__flush_work(work, true) to synchronously wait for any currently
executing instance of the work item to finish, the flush_workqueue()
becomes redundant and should be removed.

This bug was identified through static analysis. To reproduce the issue
and validate the fix, I simulated the cnic PCI device in QEMU and
introduced intentional delays — such as inserting calls to ssleep()
within the cnic_delete_task() function — to increase the likelihood
of triggering the bug.

## References
- https://git.kernel.org/stable/c/0405055930264ea8fd26f4131466fa7652e5e47d
- https://git.kernel.org/stable/c/0627e1481676669cae2df0d85b5ff13e7d24c390
- https://git.kernel.org/stable/c/6e33a7eed587062ca8161ad1f4584882a860d697
- https://git.kernel.org/stable/c/7b6a5b0a6b392263c3767fc945b311ea04b34bbd
- https://git.kernel.org/stable/c/8eeb2091e72d75df8ceaa2172638d61b4cf8929a
- https://git.kernel.org/stable/c/cfa7d9b1e3a8604afc84e9e51d789c29574fb216
- https://git.kernel.org/stable/c/e1fcd4a9c09feac0902a65615e866dbf22616125
- https://git.kernel.org/stable/c/fde6e73189f40ebcf0633aed2b68e731c25f3aa3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39945.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39945
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
