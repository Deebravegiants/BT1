# [H] mm: blk-cgroup: fix use-after-free in cgwb_release_workfn()

## Summary
Severity: High
Advisory: CVE-2026-31586
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31586
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: blk-cgroup: fix use-after-free in cgwb_release_workfn()

cgwb_release_workfn() calls css_put(wb->blkcg_css) and then later accesses
wb->blkcg_css again via blkcg_unpin_online().  If css_put() drops the last
reference, the blkcg can be freed asynchronously (css_free_rwork_fn ->
blkcg_css_free -> kfree) before blkcg_unpin_online() dereferences the
pointer to access blkcg->online_pin, resulting in a use-after-free:

  BUG: KASAN: slab-use-after-free in blkcg_unpin_online (./include/linux/instrumented.h:112 ./include/linux/atomic/atomic-instrumented.h:400 ./include/linux/refcount.h:389 ./include/linux/refcount.h:432 ./include/linux/refcount.h:450 block/blk-cgroup.c:1367)
  Write of size 4 at addr ff11000117aa6160 by task kworker/71:1/531
   Workqueue: cgwb_release cgwb_release_workfn
   Call Trace:
    <TASK>
     blkcg_unpin_online (./include/linux/instrumented.h:112 ./include/linux/atomic/atomic-instrumented.h:400 ./include/linux/refcount.h:389 ./include/linux/refcount.h:432 ./include/linux/refcount.h:450 block/blk-cgroup.c:1367)
     cgwb_release_workfn (mm/backing-dev.c:629)
     process_scheduled_works (kernel/workqueue.c:3278 kernel/workqueue.c:3385)

   Freed by task 1016:
    kfree (./include/linux/kasan.h:235 mm/slub.c:2689 mm/slub.c:6246 mm/slub.c:6561)
    css_free_rwork_fn (kernel/cgroup/cgroup.c:5542)
    process_scheduled_works (kernel/workqueue.c:3302 kernel/workqueue.c:3385)

** Stack based on commit 66672af7a095 ("Add linux-next specific files
for 20260410")

I am seeing this crash sporadically in Meta fleet across multiple kernel
versions.  A full reproducer is available at:
https://github.com/leitao/debug/blob/main/reproducers/repro_blkcg_uaf.sh

(The race window is narrow.  To make it easily reproducible, inject a
msleep(100) between css_put() and blkcg_unpin_online() in
cgwb_release_workfn().  With that delay and a KASAN-enabled kernel, the
reproducer triggers the splat reliably in less than a second.)

Fix this by moving blkcg_unpin_online() before css_put(), so the
cgwb's CSS reference keeps the blkcg alive while blkcg_unpin_online()
accesses it.

## References
- https://git.kernel.org/stable/c/115a5266749dcde7fe4127e8623d19c752088f69
- https://git.kernel.org/stable/c/1bd36e93b542d9dd020190c6607c6a3663405195
- https://git.kernel.org/stable/c/23acef4156c260e8598397a1a2e8b3a23e919893
- https://git.kernel.org/stable/c/50879a3c1faf06e661090015d59e2127255cff27
- https://git.kernel.org/stable/c/67cb119d32f35e32acd0393bbeb318b2bb1fdafe
- https://git.kernel.org/stable/c/740ba1ebb223f137ff088ab74d533a13f9167bd8
- https://git.kernel.org/stable/c/8f5857be99f1ed1fa80991c72449541f634626ee
- https://git.kernel.org/stable/c/dfc8292a1d6782c76b626315605e0585a5a18447
- https://git.kernel.org/stable/c/ea3af09eb87d8f8708c66747fcf1a2762902e839
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31586.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31586
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
