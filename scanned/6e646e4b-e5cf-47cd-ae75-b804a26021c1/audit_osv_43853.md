# [M] Evidently UI Path Traversal via Dataset Materialization Filename

## Summary
Severity: Medium
Advisory: CVE-2026-75111
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75111
Type: osv

## Details
Evidently UI fails to properly validate the filename parameter in the dataset materialization endpoint, allowing unauthenticated attackers to read arbitrary files outside the workspace directory. Attackers can supply traversal sequences or absolute paths in the filename field to access system files, which are then materialized into datasets and retrieved through the download endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75111.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75111
- https://www.vulncheck.com/advisories/evidently-ui-path-traversal-via-dataset-materialization-filename
- https://github.com/evidentlyai/evidently/issues/1887
- https://github.com/evidentlyai/evidently
- https://github.com/evidentlyai/evidently/blob/main/src/evidently/ui/service/datasets/data_source.py
