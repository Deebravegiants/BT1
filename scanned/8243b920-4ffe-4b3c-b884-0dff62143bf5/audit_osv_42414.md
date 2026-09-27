# [H] drm/amdgpu: fix division by zero with invalid uvd dimensions

## Summary
Severity: High
Advisory: CVE-2026-68106
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68106
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix division by zero with invalid uvd dimensions

When width or height is less than 16, width_in_mb or height_in_mb
becomes 0, leading to fs_in_mb being 0. This causes a division by
zero when calculating num_dpb_buffer in H264 and H264 Perf decode
paths.

Add validation to reject frames with width < 16 or height < 16
before performing any calculations that depend on these values.

V2: Format change - move up all vaiable definitions.
V3: Use warn_once to avoid spam.

(cherry picked from commit 3e41d26c70b0a459d041cc19482a226c4b7423cb)

## References
- https://git.kernel.org/stable/c/004d0453cfef16f056cb7b8bc04f69f19cf9df32
- https://git.kernel.org/stable/c/00ee64910ecf748cc15b23bbcbea472c203ec1e8
- https://git.kernel.org/stable/c/0c01c811be47e6b146552dd59bfedbea8f09b8f4
- https://git.kernel.org/stable/c/52f9a588296432accf2982f7d258192a37562f4f
- https://git.kernel.org/stable/c/81c9b4921f62d1642b9d775524ae9240e521a5ed
- https://git.kernel.org/stable/c/a00946b5ab7c25da5685ca9c58f50ff6f43c0fdf
- https://git.kernel.org/stable/c/be725ab23aa45c11a5afef3e2a9f6d8c084ae5dc
- https://git.kernel.org/stable/c/ffb33d466a68cea3e8a3dbed04d79037a3cbabd1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68106.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68106
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
