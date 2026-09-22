# [H] octeon_ep: Add SKB allocation failures handling in __octep_oq_process_rx()

## Summary
Severity: High
Advisory: CVE-2024-50145
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50145
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeon_ep: Add SKB allocation failures handling in __octep_oq_process_rx()

build_skb() returns NULL in case of a memory allocation failure so handle
it inside __octep_oq_process_rx() to avoid NULL pointer dereference.

__octep_oq_process_rx() is called during NAPI polling by the driver. If
skb allocation fails, keep on pulling packets out of the Rx DMA queue: we
shouldn't break the polling immediately and thus falsely indicate to the
octep_napi_poll() that the Rx pressure is going down. As there is no
associated skb in this case, don't process the packets and don't push them
up the network stack - they are skipped.

Helper function is implemented to unmmap/flush all the fragment buffers
used by the dropped packet. 'alloc_failures' counter is incremented to
mark the skb allocation error in driver statistics.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/09ce491112bbf0b866e2638d3e961c1c73d1f00b
- https://git.kernel.org/stable/c/2dedcb6f99f4c1a11944e7cc35dbeb9b18a5cbac
- https://git.kernel.org/stable/c/c2d2dc4f88bb3cfc4f3cc320fd3ff51b0ae5b0ea
- https://git.kernel.org/stable/c/eb592008f79be52ccef88cd9a5249b3fc0367278
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50145.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50145
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
