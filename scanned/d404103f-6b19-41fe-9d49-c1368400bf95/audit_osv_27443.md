# [M] CVE-2024-21575

## Summary
Severity: Medium
Advisory: CVE-2024-21575
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2024-12-12
Source: https://osv.dev/vulnerability/CVE-2024-21575
Type: osv

## Details
ComfyUI-Impact-Pack is vulnerable to Path Traversal. The issue stems from missing validation of the `image.filename` field in a POST request sent to the `/upload/temp` endpoint added by the extension to the server. This results in writing arbitrary files to the file system which may, under some conditions, result in remote code execution (RCE).

## References
- https://github.com/ltdrdata/ComfyUI-Impact-Pack/blob/1087f2ee063c9d53cd198add79b41a7a3465c05a/modules/impact/impact_server.py#L28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21575.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-21575
- https://github.com/ltdrdata/ComfyUI-Impact-Pack/commit/a43dae373e648ae0f0cc0c9768c3cea6a72acff7
