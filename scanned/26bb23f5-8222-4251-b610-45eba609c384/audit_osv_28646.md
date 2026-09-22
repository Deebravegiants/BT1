# [M] dmaengine: fsl-qdma: Fix a memory leak related to the queue command DMA

## Summary
Severity: Medium
Advisory: CVE-2024-35833
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35833
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.78, >=6.2.0 <6.6.17, >=6.7.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: fsl-qdma: Fix a memory leak related to the queue command DMA

This dma_alloc_coherent() is undone neither in the remove function, nor in
the error handling path of fsl_qdma_probe().

Switch to the managed version to fix both issues.

## References
- https://git.kernel.org/stable/c/15eb996d7d13cb72a16389231945ada8f0fef2c3
- https://git.kernel.org/stable/c/198270de9d8eb3b5d5f030825ea303ef95285d24
- https://git.kernel.org/stable/c/1c75fe450b5200c78f4a102a0eb8e15d8f1ccda8
- https://git.kernel.org/stable/c/25ab4d72eb7cbfa0f3d97a139a9b2bfcaa72dd59
- https://git.kernel.org/stable/c/3aa58cb51318e329d203857f7a191678e60bb714
- https://git.kernel.org/stable/c/5cd8a51517ce15edbdcea4fc74c4c127ddaa1bd6
- https://git.kernel.org/stable/c/ae6769ba51417c1c86fb645812d5bff455eee802
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35833.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35833
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
