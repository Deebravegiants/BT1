# [H] drm/amdgpu/vcn: set no_user_fence for VCN v5.0.1 enc ring

## Summary
Severity: High
Advisory: CVE-2026-63849
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63849
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu/vcn: set no_user_fence for VCN v5.0.1 enc ring

VCN encoder and decoder rings do not support 64-bit user fence writes,
reject CS submissions with user fences.

(cherry picked from commit e16be95a2c3ee712b142cb27d2dca0b461181359)

## References
- https://git.kernel.org/stable/c/081ef0e46c9cdd26c0db0ef721470393d36b6655
- https://git.kernel.org/stable/c/5a4bffd67e94944ed3db26a959346cfb7fabaecd
- https://git.kernel.org/stable/c/8f4954722eab88e10c4ea0c0d3b1269c31421d3a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63849.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63849
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
