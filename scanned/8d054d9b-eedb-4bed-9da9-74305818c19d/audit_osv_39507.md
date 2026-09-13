# [H] drm/nouveau: fix u32 overflow in pushbuf reloc bounds check

## Summary
Severity: High
Advisory: CVE-2026-46006
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46006
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.259, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/nouveau: fix u32 overflow in pushbuf reloc bounds check

nouveau_gem_pushbuf_reloc_apply() validates each relocation with

    if (r->reloc_bo_offset + 4 > nvbo->bo.base.size)

but reloc_bo_offset is __u32 (uapi/drm/nouveau_drm.h) and the integer
literal 4 promotes to unsigned int, so the addition is performed in 32
bits and wraps before the comparison against the size_t bo size.

Cast to u64 so the addition happens in 64-bit arithmetic.

[ Add Fixes: tag. - Danilo ]

## References
- https://git.kernel.org/stable/c/2fc87d37be1b730a149b035f9375fdb8cc5333a5
- https://git.kernel.org/stable/c/332884f5eb79dd60a7162b079d09d39208567a31
- https://git.kernel.org/stable/c/3429275684f4bad42876955301f3c5c814aae909
- https://git.kernel.org/stable/c/45a45184b9c0b0b26ead06e370cda2073616a7cc
- https://git.kernel.org/stable/c/573a1104bd36e49c067a9dc62e7c476d5ee7e92a
- https://git.kernel.org/stable/c/d749a9a0ee4014681487e7ae549901aa8c176637
- https://git.kernel.org/stable/c/e441d5c23ec644c8d27593db3b8928e8933512a9
- https://git.kernel.org/stable/c/fa297e919d1680c38ab268ff952b1698dac987f6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46006.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46006
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
