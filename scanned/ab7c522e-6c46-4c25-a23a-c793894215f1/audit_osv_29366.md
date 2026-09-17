# [H] drm/amd/display: ASSERT when failing to find index by plane/stream id

## Summary
Severity: High
Advisory: CVE-2024-42117
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42117
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: ASSERT when failing to find index by plane/stream id

[WHY]
find_disp_cfg_idx_by_plane_id and find_disp_cfg_idx_by_stream_id returns
an array index and they return -1 when not found; however, -1 is not a
valid index number.

[HOW]
When this happens, call ASSERT(), and return a positive number (which is
fewer than callers' array size) instead.

This fixes 4 OVERRUN and 2 NEGATIVE_RETURNS issues reported by Coverity.

## References
- https://git.kernel.org/stable/c/01eb50e53c1ce505bf449348d433181310288765
- https://git.kernel.org/stable/c/a9c047a5cf3135b8b66bd28fbe2c698b9cace0b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42117.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42117
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
