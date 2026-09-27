# [C] virtio-net: fix overflow inside virtnet_rq_alloc

## Summary
Severity: Critical
Advisory: CVE-2024-57843
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57843
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio-net: fix overflow inside virtnet_rq_alloc

When the frag just got a page, then may lead to regression on VM.
Specially if the sysctl net.core.high_order_alloc_disable value is 1,
then the frag always get a page when do refill.

Which could see reliable crashes or scp failure (scp a file 100M in size
to VM).

The issue is that the virtnet_rq_dma takes up 16 bytes at the beginning
of a new frag. When the frag size is larger than PAGE_SIZE,
everything is fine. However, if the frag is only one page and the
total size of the buffer and virtnet_rq_dma is larger than one page, an
overflow may occur.

The commit f9dac92ba908 ("virtio_ring: enable premapped mode whatever
use_dma_api") introduced this problem. And we reverted some commits to
fix this in last linux version. Now we try to enable it and fix this
bug directly.

Here, when the frag size is not enough, we reduce the buffer len to fix
this problem.

## References
- https://git.kernel.org/stable/c/67a11de8965c2ab19e215fb6651d44847e068614
- https://git.kernel.org/stable/c/6aacd1484468361d1d04badfe75f264fa5314864
- https://git.kernel.org/stable/c/a8f7d6963768b114ec9644ff0148dde4c104e84b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57843.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57843
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
