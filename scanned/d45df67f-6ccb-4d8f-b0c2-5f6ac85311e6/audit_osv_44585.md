# [M] facefusion before 3.7.0 Path Traversal via Job Identifier

## Summary
Severity: Medium
Advisory: CVE-2026-84702
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84702
Type: osv

## Details
facefusion through 3.6.1 fails to normalize job identifiers in get_job_file_name, allowing attackers to write files outside the jobs directory. Attackers can supply traversal sequences in the job identifier parameter through the unauthenticated HTTP API to create files at arbitrary locations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84702.json
- https://github.com/facefusion/facefusion/releases/tag/3.7.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-84702
- https://www.vulncheck.com/advisories/facefusion-before-3.7.0-path-traversal-via-job-identifier
- https://github.com/facefusion/facefusion/commit/a2cbfd73b10191e51ed2eb1e83c19121153e0a22
- https://github.com/facefusion/facefusion
- https://github.com/facefusion/facefusion/blob/3.6.1/facefusion/jobs/job_manager.py
- https://github.com/geo-chen/oss/blob/main/facefusion.md
