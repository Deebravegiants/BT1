# [H] CVE-2025-60467

## Summary
Severity: High
Advisory: CVE-2025-60467
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2025-60467
Type: osv

## Details
A use-after-free in the gf_filter_pid_inst_swap_delete_task function (/filter_core/filter_pid.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted media file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/27/4
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/37/37_gf_filter_pid_inst_swap_delete_task_filter_core_filter_pid_c_574
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/37/README.md
- https://infosec.exchange/@sigdevel/116780518074911144
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60467.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60467
- https://github.com/gpac/gpac/issues/3286
- https://github.com/gpac/gpac/commit/976dacf65cb6986a4e4f350fb8d3ed0a17dc3a77
