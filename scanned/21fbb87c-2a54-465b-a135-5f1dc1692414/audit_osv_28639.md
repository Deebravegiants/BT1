# [H] drm/amdgpu: amdgpu_ttm_gart_bind set gtt bound flag

## Summary
Severity: High
Advisory: CVE-2024-35817
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35817
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: amdgpu_ttm_gart_bind set gtt bound flag

Otherwise after the GTT bo is released, the GTT and gart space is freed
but amdgpu_ttm_backend_unbind will not clear the gart page table entry
and leave valid mapping entry pointing to the stale system page. Then
if GPU access the gart address mistakely, it will read undefined value
instead page fault, harder to debug and reproduce the real issue.

## References
- https://git.kernel.org/stable/c/589c414138a1bed98e652c905937d8f790804efe
- https://git.kernel.org/stable/c/5cdce3dda3b3dacde902f63a8ee72c2b7f91912d
- https://git.kernel.org/stable/c/5d5f1a7f3b1039925f79c7894f153c2a905201fb
- https://git.kernel.org/stable/c/6c6064cbe58b43533e3451ad6a8ba9736c109ac3
- https://git.kernel.org/stable/c/6fcd12cb90888ef2d8af8d4c04e913252eee4ef3
- https://git.kernel.org/stable/c/e8d27caef2c829a306e1f762fb95f06e8ec676f6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35817.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35817
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
