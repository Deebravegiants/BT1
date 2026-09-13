# [M] CVE-2025-60477

## Summary
Severity: Medium
Advisory: CVE-2025-60477
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2025-60477
Type: osv

## Details
A NULL pointer dereference in the gf_filter_pid_resolve_file_template_ex function (/filter_core/filter_pid.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted file.

## References
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/48/README.md
- https://infosec.exchange/@sigdevel/116658486442433074
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60477.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60477
- https://github.com/gpac/gpac/issues/3301
- https://github.com/gpac/gpac/commit/13eb5b76560aaf7813b865a2ad433258478e2695
