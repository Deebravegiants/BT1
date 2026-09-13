# [H] drm/amdgpu: reject oversized IBs with per-ring packet limits

## Summary
Severity: High
Advisory: CVE-2026-80576
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80576
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: reject oversized IBs with per-ring packet limits

On GFX rings, amdgpu_cs_p2_ib() passed user-supplied ib_bytes through
to ib->length_dw without a limit, while ring_emit_ib() encodes length
into packet fields. Oversized values can corrupt adjacent control bits
and destabilize command submission.

Add a per-ring IB packet size limit helper and reject command
submissions exceeding the corresponding dword limit before IB
allocation. Use the documented 20-bit limit for GFX/compute/SDMA/VPE,
and apply the MM fallback limit for other ring types.

(cherry picked from commit 7f48fa2cf62e3fa6c9c3870aa74988f773247e52)

## References
- https://git.kernel.org/stable/c/07fe270ec07c138a70afe7a81e115a85c35c545c
- https://git.kernel.org/stable/c/1474f3970d1afd303e12ff14d06808eabb371576
- https://git.kernel.org/stable/c/6e164ba1057175fb8a370d8e05cbff5c57eac0c8
- https://git.kernel.org/stable/c/fd37f9dd5b5ab70a46fa7bc76623c0528d602b27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80576.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80576
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
