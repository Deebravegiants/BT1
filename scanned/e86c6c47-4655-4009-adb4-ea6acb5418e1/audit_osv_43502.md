# [C] crypto: marvell/octeontx - fix DMA cleanup using wrong loop index

## Summary
Severity: Critical
Advisory: CVE-2026-74280
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74280
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: marvell/octeontx - fix DMA cleanup using wrong loop index

The sg_cleanup path used list[i] instead of list[j] when unmapping DMA
buffers, leaking successfully mapped entries and repeatedly unmapping
the failed one.

## References
- https://git.kernel.org/stable/c/5f99a396f706afc749448659d1565991330e4f71
- https://git.kernel.org/stable/c/6c721a3e43344f8560ee4ef506fc1f72b4646dcd
- https://git.kernel.org/stable/c/7891c64c0520519782470ba29bac8a5761e295d8
- https://git.kernel.org/stable/c/8a0db9fad3c97e6447a92417cb95d7c55eaa9530
- https://git.kernel.org/stable/c/8d301e5a51173ba56ce4f632a2a33bf6b14b0fcf
- https://git.kernel.org/stable/c/97f150ba3e372256eabb93bd80c2cf3740077fb5
- https://git.kernel.org/stable/c/acff30cfc0d72465b51b0bfdf019f1cb54e15314
- https://git.kernel.org/stable/c/ed374dbc70c10c4a864414b3d9c257faec8fd485
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74280.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74280
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
