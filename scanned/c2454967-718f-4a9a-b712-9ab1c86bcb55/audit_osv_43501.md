# [C] crypto: cavium/cpt - fix DMA cleanup using wrong loop index

## Summary
Severity: Critical
Advisory: CVE-2026-74279
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74279
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: cavium/cpt - fix DMA cleanup using wrong loop index

The sg_cleanup error path used list[i] instead of list[j] when unmapping
DMA buffers, leaking successfully mapped entries and repeatedly unmapping
the failed one.

## References
- https://git.kernel.org/stable/c/23c6174e48f66fc10b998b0acdb406cb0caf5c80
- https://git.kernel.org/stable/c/23d3a7e896a1fe2d7a6bcb42f093948b79f8a198
- https://git.kernel.org/stable/c/28141f95ae93b18f9bfde953cb787fcb151fb9da
- https://git.kernel.org/stable/c/3b8a1e1f4e4071a62b20374028744e8cc8310d48
- https://git.kernel.org/stable/c/8afd1007ef79898a6e010eaade97097e49405fce
- https://git.kernel.org/stable/c/9dbf173bd32d5f81b005008b682bfb50aa093455
- https://git.kernel.org/stable/c/d319b83b97b3585550d9ae592dfa78c755b6129e
- https://git.kernel.org/stable/c/fb4d57b83356d4bd411b45ede3024e0ff42c9b5e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74279.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74279
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
