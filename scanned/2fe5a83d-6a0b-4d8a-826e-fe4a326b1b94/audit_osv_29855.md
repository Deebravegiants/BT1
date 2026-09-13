# [M] dma-debug: fix a possible deadlock on radix_lock

## Summary
Severity: Medium
Advisory: CVE-2024-47143
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-47143
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma-debug: fix a possible deadlock on radix_lock

radix_lock() shouldn't be held while holding dma_hash_entry[idx].lock
otherwise, there's a possible deadlock scenario when
dma debug API is called holding rq_lock():

CPU0                   CPU1                       CPU2
dma_free_attrs()
check_unmap()          add_dma_entry()            __schedule() //out
                                                  (A) rq_lock()
get_hash_bucket()
(A) dma_entry_hash
                                                  check_sync()
                       (A) radix_lock()           (W) dma_entry_hash
dma_entry_free()
(W) radix_lock()
                       // CPU2's one
                       (W) rq_lock()

CPU1 situation can happen when it extending radix tree and
it tries to wake up kswapd via wake_all_kswapd().

CPU2 situation can happen while perf_event_task_sched_out()
(i.e. dma sync operation is called while deleting perf_event using
 etm and etr tmc which are Arm Coresight hwtracing driver backends).

To remove this possible situation, call dma_entry_free() after
put_hash_bucket() in check_unmap().

## References
- https://git.kernel.org/stable/c/3ccce34a5c3f5c9541108a451657ade621524b32
- https://git.kernel.org/stable/c/7543c3e3b9b88212fcd0aaf5cab5588797bdc7de
- https://git.kernel.org/stable/c/8c1b4fea8d62285f5e1a8194889b39661608bd8a
- https://git.kernel.org/stable/c/c212d91070beca0d03fef7bf988baf4ff4b3eee4
- https://git.kernel.org/stable/c/efe1b9bbf356357fdff0399af361133d6e3ba18e
- https://git.kernel.org/stable/c/f2b95248a16c5186d1c658fc0aeb2f3bd95e5259
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47143.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47143
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
