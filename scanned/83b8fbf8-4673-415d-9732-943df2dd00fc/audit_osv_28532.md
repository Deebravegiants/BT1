# [H] CVE-2024-34193

## Summary
Severity: High
Advisory: CVE-2024-34193
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-34193
Type: osv

## Details
smanga 3.2.7 does not filter the file parameter at the PHP/get file flow.php interface, resulting in a path traversal vulnerability that can cause arbitrary file reading.

## References
- https://github.com/vulreport3r/cve-reports/blob/main/Smanga_has_an_arbitrary_file_read_vulnerability/report.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34193.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34193
