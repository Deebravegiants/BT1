# [H] drm/amd/display: Don't treat wb connector as physical in create_validate_stream_for_sink

## Summary
Severity: High
Advisory: CVE-2025-38098
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38098
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Don't treat wb connector as physical in create_validate_stream_for_sink

Don't try to operate on a drm_wb_connector as an amdgpu_dm_connector.
While dereferencing aconnector->base will "work" it's wrong and
might lead to unknown bad things. Just... don't.

## References
- https://git.kernel.org/stable/c/18ca68f7c657721583a75cab01f0d0d2ec63a6c9
- https://git.kernel.org/stable/c/b14e726d57f61085485f107a6203c50a09695abd
- https://git.kernel.org/stable/c/cbf4890c6f28fb1ad733e14613fbd33c2004bced
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38098.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38098
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
