# [H] drm/amd/display: Fix index out of bounds in degamma hardware format translation

## Summary
Severity: High
Advisory: CVE-2024-49894
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49894
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix index out of bounds in degamma hardware format translation

Fixes index out of bounds issue in
`cm_helper_translate_curve_to_degamma_hw_format` function. The issue
could occur when the index 'i' exceeds the number of transfer function
points (TRANSFER_FUNC_POINTS).

The fix adds a check to ensure 'i' is within bounds before accessing the
transfer function points. If 'i' is out of bounds the function returns
false to indicate an error.

Reported by smatch:
drivers/gpu/drm/amd/amdgpu/../display/dc/dcn10/dcn10_cm_common.c:594 cm_helper_translate_curve_to_degamma_hw_format() error: buffer overflow 'output_tf->tf_pts.red' 1025 <= s32max
drivers/gpu/drm/amd/amdgpu/../display/dc/dcn10/dcn10_cm_common.c:595 cm_helper_translate_curve_to_degamma_hw_format() error: buffer overflow 'output_tf->tf_pts.green' 1025 <= s32max
drivers/gpu/drm/amd/amdgpu/../display/dc/dcn10/dcn10_cm_common.c:596 cm_helper_translate_curve_to_degamma_hw_format() error: buffer overflow 'output_tf->tf_pts.blue' 1025 <= s32max

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/07078fa5d589a7fbce8f81ea8acf7aa0021ab38e
- https://git.kernel.org/stable/c/122e3a7a8c7bcbe3aacddd6103f67f9f36bed473
- https://git.kernel.org/stable/c/2495c8e272d84685403506833a664fad932e453a
- https://git.kernel.org/stable/c/2f5da549535be8ccd2ab7c9abac8562ad370b181
- https://git.kernel.org/stable/c/b3dfa878257a7e98830b3009ca5831a01d8f85fc
- https://git.kernel.org/stable/c/b7e99058eb2e86aabd7a10761e76cae33d22b49f
- https://git.kernel.org/stable/c/c130a3c09e3746c1a09ce26c20d21d449d039b1d
- https://git.kernel.org/stable/c/c6979719012a90e5b8e3bc31725fbfdd0b9b2b79
- https://git.kernel.org/stable/c/f5f6d90087131812c1e4b9d3103f400f1624396d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49894.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49894
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
