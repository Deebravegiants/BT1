# [H] vhost: fix vhost_get_avail_idx for a non empty ring

## Summary
Severity: High
Advisory: CVE-2026-74356
Ecosystem: Linux
CVSS: 7.4 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74356
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost: fix vhost_get_avail_idx for a non empty ring

vhost_get_avail_idx is supposed to report whether it has updated
vq->avail_idx. Instead, it returns whether all entries have been
consumed, which is usually the same. But not always - in
drivers/vhost/net.c and when mergeable buffers have been enabled, the
driver checks whether the combined entries are big enough to store an
incoming packet. If not, the driver re-enables notifications with
available entries still in the ring. The incorrect return value from
vhost_get_avail_idx propagates through vhost_enable_notify and causes
the host to livelock if the guest is not making progress, as vhost will
immediately disable notifications and retry using the available entries.

This goes back to commit d3bb267bbdcb ("vhost: cache avail index in
vhost_enable_notify()") which changed vhost_enable_notify() to compare
the freshly read avail index against vq->last_avail_idx instead of the
previously cached vq->avail_idx. Commit 7ad472397667 ("vhost: move
smp_rmb() into vhost_get_avail_idx()") then carried over the same
comparison when refactoring vhost_enable_notify() to call the unified
vhost_get_avail_idx().

The obvious fix is to make vhost_get_avail_idx do what the comment
says it does and report whether new entries have been added.

## References
- https://git.kernel.org/stable/c/09861858a68342f851f71c669ac0f69865c32151
- https://git.kernel.org/stable/c/7f229d27bf27c7e589eca690d8612763a7a4801f
- https://git.kernel.org/stable/c/a9326b652bc7acd748d7a1143573845c7924d847
- https://git.kernel.org/stable/c/e115471008111f894c6528d9ab2ce7d0ce306f35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74356.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74356
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
