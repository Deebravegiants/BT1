# [H] drm/radeon: check bo_va->bo is non-NULL before using it

## Summary
Severity: High
Advisory: CVE-2024-41060
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41060
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.10.234, >=5.11.0 <5.15.164, >=5.16.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/radeon: check bo_va->bo is non-NULL before using it

The call to radeon_vm_clear_freed might clear bo_va->bo, so
we have to check it before dereferencing it.

## References
- https://git.kernel.org/stable/c/6fb15dcbcf4f212930350eaee174bb60ed40a536
- https://git.kernel.org/stable/c/8a500b3a5f0a58c6f99039091fbd715f64f2f8af
- https://git.kernel.org/stable/c/a2b201f83971df03c8e81a480b2f2846ae8ce1a3
- https://git.kernel.org/stable/c/a9100f17428cb733c4f6fbb132d98bed76318342
- https://git.kernel.org/stable/c/e8d3c53c6f1cccea9c03113f06dd39521c228831
- https://git.kernel.org/stable/c/f13c96e0e325a057c03f8a47734adb360e112efe
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41060.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41060
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
