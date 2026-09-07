# [M] keras Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cjgq-5qmw-rcj6
CVE: CVE-2024-55459
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-01-08
Source: https://github.com/advisories/GHSA-cjgq-5qmw-rcj6
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=0

## Details
An issue in keras 3.7.0 allows attackers to write arbitrary files to the user's machine via downloading a crafted tar file through the get_file function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55459
- https://github.com/keras-team/keras
- https://github.com/keras-team/keras/blob/8f5592bcb61ff48c96560c8923e482db1076b54a/keras/src/utils/file_utils.py#L115
- https://github.com/pypa/advisory-database/tree/main/vulns/keras/PYSEC-2025-121.yaml
- https://keras.io
- https://river-bicycle-f1e.notion.site/Arbitrary-File-Write-Vulnerability-in-get_file-function-11888e31952580179224e50892976d32
