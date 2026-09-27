# [C] Tooxie Shiva 0.10.0 allows absolute path traversal because Flask send_file function used unsafely

## Summary
Severity: Critical
Advisory: GHSA-qp72-96p2-g644
CVE: CVE-2022-31558
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2022-07-12
Source: https://github.com/advisories/GHSA-qp72-96p2-g644
Type: github-advisory

## Affected
- PyPI: `shiva` — affected >=0

## Details
The tooxie/shiva-server repository through 0.10.0 on GitHub allows absolute path traversal because the Flask send_file function is used unsafely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31558
- https://github.com/tooxie/shiva-server/issues/189
- https://github.com/tooxie/shiva-server
