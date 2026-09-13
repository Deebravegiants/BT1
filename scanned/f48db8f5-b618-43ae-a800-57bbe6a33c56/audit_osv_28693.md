# [M] dma-buf: Fix NULL pointer dereference in sanitycheck()

## Summary
Severity: Medium
Advisory: CVE-2024-35916
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35916
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma-buf: Fix NULL pointer dereference in sanitycheck()

If due to a memory allocation failure mock_chain() returns NULL, it is
passed to dma_fence_enable_sw_signaling() resulting in NULL pointer
dereference there.

Call dma_fence_enable_sw_signaling() only if mock_chain() succeeds.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/0336995512cdab0c65e99e4cdd47c4606debe14e
- https://git.kernel.org/stable/c/156c226cbbdcf5f3bce7b2408a33b59fab7fae2c
- https://git.kernel.org/stable/c/2295bd846765c766701e666ed2e4b35396be25e6
- https://git.kernel.org/stable/c/eabf131cba1db12005a68378305f13b9090a7a6b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35916.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35916
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
