# [M] virtio-blk: don't keep queue frozen during system suspend

## Summary
Severity: Medium
Advisory: CVE-2024-57946
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-57946
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.289, >=5.5.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.123, >=6.2.0 <6.6.69, >=6.7.0 <6.12.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio-blk: don't keep queue frozen during system suspend

Commit 4ce6e2db00de ("virtio-blk: Ensure no requests in virtqueues before
deleting vqs.") replaces queue quiesce with queue freeze in virtio-blk's
PM callbacks. And the motivation is to drain inflight IOs before suspending.

block layer's queue freeze looks very handy, but it is also easy to cause
deadlock, such as, any attempt to call into bio_queue_enter() may run into
deadlock if the queue is frozen in current context. There are all kinds
of ->suspend() called in suspend context, so keeping queue frozen in the
whole suspend context isn't one good idea. And Marek reported lockdep
warning[1] caused by virtio-blk's freeze queue in virtblk_freeze().

[1] https://lore.kernel.org/linux-block/ca16370e-d646-4eee-b9cc-87277c89c43c@samsung.com/

Given the motivation is to drain in-flight IOs, it can be done by calling
freeze & unfreeze, meantime restore to previous behavior by keeping queue
quiesced during suspend.

## References
- https://git.kernel.org/stable/c/12c0ddd6c551c1e438b087f874b4f1223a75f7ea
- https://git.kernel.org/stable/c/6dea8e3de59928974bf157dd0499d3958d744ae4
- https://git.kernel.org/stable/c/7678abee0867e6b7fb89aa40f6e9f575f755fb37
- https://git.kernel.org/stable/c/92d5139b91147ab372a17daf5dc27a5b9278e516
- https://git.kernel.org/stable/c/9ca428c6397abaa8c38f5c69133a2299e1efbbf2
- https://git.kernel.org/stable/c/9e323f856cf4963120e0e3892a84ef8bd764a0e4
- https://git.kernel.org/stable/c/d738f3215bb4f88911ff4579780a44960c8e0ca5
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57946.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57946
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
