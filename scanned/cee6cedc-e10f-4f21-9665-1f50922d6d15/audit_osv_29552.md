# [H] dma: fix call order in dmam_free_coherent

## Summary
Severity: High
Advisory: CVE-2024-43856
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-43856
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.21 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma: fix call order in dmam_free_coherent

dmam_free_coherent() frees a DMA allocation, which makes the
freed vaddr available for reuse, then calls devres_destroy()
to remove and free the data structure used to track the DMA
allocation. Between the two calls, it is possible for a
concurrent task to make an allocation with the same vaddr
and add it to the devres list.

If this happens, there will be two entries in the devres list
with the same vaddr and devres_destroy() can free the wrong
entry, triggering the WARN_ON() in dmam_match.

Fix by destroying the devres entry before freeing the DMA
allocation.

  kokonut //net/encryption
    http://sponge2/b9145fe6-0f72-4325-ac2f-a84d81075b03

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/1fe97f68fce1ba24bf823bfb0eb0956003473130
- https://git.kernel.org/stable/c/22094f5f52e7bc16c5bf9613365049383650b02e
- https://git.kernel.org/stable/c/257193083e8f43907e99ea633820fc2b3bcd24c7
- https://git.kernel.org/stable/c/28e8b7406d3a1f5329a03aa25a43aa28e087cb20
- https://git.kernel.org/stable/c/2f7bbdc744f2e7051d1cb47c8e082162df1923c9
- https://git.kernel.org/stable/c/87b34c8c94e29fa01d744e5147697f592998d954
- https://git.kernel.org/stable/c/f993a4baf6b622232e4c190d34c220179e5d61eb
- https://git.kernel.org/stable/c/fe2d246080f035e0af5793cb79067ba125e4fb63
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43856.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43856
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
