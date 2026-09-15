# [M] mtd: rawnand: atmel: fix refcount issue in atmel_nand_controller_init

## Summary
Severity: Medium
Advisory: CVE-2022-49212
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49212
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: rawnand: atmel: fix refcount issue in atmel_nand_controller_init

The reference counting issue happens in several error handling paths
on a refcounted object "nc->dmac". In these paths, the function simply
returns the error code, forgetting to balance the reference count of
"nc->dmac", increased earlier by dma_request_channel(), which may
cause refcount leaks.

Fix it by decrementing the refcount of specific object in those error
paths.

## References
- https://git.kernel.org/stable/c/0856bf27057561f42b37df111603cf5a0d040294
- https://git.kernel.org/stable/c/8baea2b96fa90af8d0f937caf4cf2105ee094d93
- https://git.kernel.org/stable/c/9843c9c98f26c6ad843260b19bfdaa2598f2ae1e
- https://git.kernel.org/stable/c/9b08d211db4c447eb1a07df65e45e0aa772e0fa6
- https://git.kernel.org/stable/c/a3587259ae553e41d1ce8c7435351a5d6b299a11
- https://git.kernel.org/stable/c/f1694169f3674cdf7553aed06864254635679878
- https://git.kernel.org/stable/c/fe0e2ce5c87e9c0b9485ff566362030aa55972cf
- https://git.kernel.org/stable/c/fecbd4a317c95d73c849648c406bcf1b6a0ec1cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49212.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49212
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
