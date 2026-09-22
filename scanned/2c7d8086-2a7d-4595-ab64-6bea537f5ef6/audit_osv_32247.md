# [H] CVE-2025-26520

## Summary
Severity: High
Advisory: CVE-2025-26520
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-26520
Type: osv

## Details
Cacti through 1.2.29 allows SQL injection in the template function in host_templates.php via the graph_template parameter. NOTE: this issue exists because of an incomplete fix for CVE-2024-54146.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26520.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-26520
- https://github.com/Cacti/cacti/commit/7fa60c03ad4a69c701ac6b77c85a8927df7acd51
- https://github.com/Cacti/cacti/pull/6096
