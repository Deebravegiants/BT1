# [H] drm/amd/display: Fix potential index out of bounds in color transformation function

## Summary
Severity: High
Advisory: CVE-2024-38552
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38552
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix potential index out of bounds in color transformation function

Fixes index out of bounds issue in the color transformation function.
The issue could occur when the index 'i' exceeds the number of transfer
function points (TRANSFER_FUNC_POINTS).

The fix adds a check to ensure 'i' is within bounds before accessing the
transfer function points. If 'i' is out of bounds, an error message is
logged and the function returns false to indicate an error.

Reported by smatch:
drivers/gpu/drm/amd/amdgpu/../display/dc/dcn10/dcn10_cm_common.c:405 cm_helper_translate_curve_to_hw_format() error: buffer overflow 'output_tf->tf_pts.red' 1025 <= s32max
drivers/gpu/drm/amd/amdgpu/../display/dc/dcn10/dcn10_cm_common.c:406 cm_helper_translate_curve_to_hw_format() error: buffer overflow 'output_tf->tf_pts.green' 1025 <= s32max
drivers/gpu/drm/amd/amdgpu/../display/dc/dcn10/dcn10_cm_common.c:407 cm_helper_translate_curve_to_hw_format() error: buffer overflow 'output_tf->tf_pts.blue' 1025 <= s32max

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/04bc4d1090c343025d69149ca669a27c5b9c34a7
- https://git.kernel.org/stable/c/123edbae64f4d21984359b99c6e79fcde31c6123
- https://git.kernel.org/stable/c/4e8c8b37ee84b3b19c448d2b8e4c916d2f5b9c86
- https://git.kernel.org/stable/c/604c506ca43fce52bb882cff9c1fdf2ec3b4029c
- https://git.kernel.org/stable/c/63ae548f1054a0b71678d0349c7dc9628ddd42ca
- https://git.kernel.org/stable/c/7226ddf3311c5e5a7726ad7d4e7b079bb3cfbb29
- https://git.kernel.org/stable/c/98b8a6bfd30d07a19cfacdf82b50f84bf3360869
- https://git.kernel.org/stable/c/ced9c4e2289a786b8fa684d8893b7045ea53ef7e
- https://git.kernel.org/stable/c/e280ab978c81443103d7c61bdd1d8d708cf6ed6d
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38552.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38552
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
