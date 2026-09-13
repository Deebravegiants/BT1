# [C] igbvf: Fix leak in TX DMA error cleanup

## Summary
Severity: Critical
Advisory: CVE-2026-74495
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74495
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

igbvf: Fix leak in TX DMA error cleanup

If an error is encountered while mapping TX buffers, the driver should
unmap any buffers already mapped for that skb.

Because count is incremented before each frag mapping, it will always
match the correct number of unmappings needed when dma_error is reached.
Decrementing count before the while loop in dma_error causes an
off-by-one error. If any mapping was successful before an unsuccessful
mapping, exactly one DMA mapping (the head) would leak.

This bug was introduced by a 2010 fix for an endless loop in dma_error.
All other affected drivers have already been fixed.

## References
- https://git.kernel.org/stable/c/0565052b7e2f436b7f1541f4849da96dc0aa7a0e
- https://git.kernel.org/stable/c/31089f4eab42e0fc248ec80c26f9b0bad59ba4cc
- https://git.kernel.org/stable/c/56726ff12cb6759ab90d6f5332c2377aeca7d249
- https://git.kernel.org/stable/c/845a9cdd9b03b7b6fa8de3ee80579780350a7f65
- https://git.kernel.org/stable/c/bc25d56c03e41c10bc4b40e99ca5d7b941675c04
- https://git.kernel.org/stable/c/df07003b5a6c6c9fce60d765d6a3da815a74c41c
- https://git.kernel.org/stable/c/e3ed89c257f6361f13df23023cd10ace830330ad
- https://git.kernel.org/stable/c/e42b7225c45f57b42306b80cdd3bda202bae7293
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74495.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74495
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
