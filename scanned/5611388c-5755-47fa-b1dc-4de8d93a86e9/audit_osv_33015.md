# [H] mm: fix a UAF when vma->mm is freed after vma->vm_refcnt got dropped

## Summary
Severity: High
Advisory: CVE-2025-38554
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38554
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: fix a UAF when vma->mm is freed after vma->vm_refcnt got dropped

By inducing delays in the right places, Jann Horn created a reproducer for
a hard to hit UAF issue that became possible after VMAs were allowed to be
recycled by adding SLAB_TYPESAFE_BY_RCU to their cache.

Race description is borrowed from Jann's discovery report:
lock_vma_under_rcu() looks up a VMA locklessly with mas_walk() under
rcu_read_lock().  At that point, the VMA may be concurrently freed, and it
can be recycled by another process.  vma_start_read() then increments the
vma->vm_refcnt (if it is in an acceptable range), and if this succeeds,
vma_start_read() can return a recycled VMA.

In this scenario where the VMA has been recycled, lock_vma_under_rcu()
will then detect the mismatching ->vm_mm pointer and drop the VMA through
vma_end_read(), which calls vma_refcount_put().  vma_refcount_put() drops
the refcount and then calls rcuwait_wake_up() using a copy of vma->vm_mm. 
This is wrong: It implicitly assumes that the caller is keeping the VMA's
mm alive, but in this scenario the caller has no relation to the VMA's mm,
so the rcuwait_wake_up() can cause UAF.

The diagram depicting the race:
T1         T2         T3
==         ==         ==
lock_vma_under_rcu
  mas_walk
          <VMA gets removed from mm>
                      mmap
                        <the same VMA is reallocated>
  vma_start_read
    __refcount_inc_not_zero_limited_acquire
                      munmap
                        __vma_enter_locked
                          refcount_add_not_zero
  vma_end_read
    vma_refcount_put
      __refcount_dec_and_test
                          rcuwait_wait_event
                            <finish operation>
      rcuwait_wake_up [UAF]

Note that rcuwait_wait_event() in T3 does not block because refcount was
already dropped by T1.  At this point T3 can exit and free the mm causing
UAF in T1.

To avoid this we move vma->vm_mm verification into vma_start_read() and
grab vma->vm_mm to stabilize it before vma_refcount_put() operation.

[surenb@google.com: v3]

## References
- https://git.kernel.org/stable/c/1bcd236a2536a451e385f8d6d2bb589689ec812f
- https://git.kernel.org/stable/c/6e88fe54721dee17d3496bc998f0c7d243896348
- https://git.kernel.org/stable/c/9bbffee67ffd16360179327b57f3b1245579ef08
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38554.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38554
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
