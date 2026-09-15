# [C] SatyaLab opendiamond 10.1.1 vulnerable to path traversal because Flask send_file function used unsafely

## Summary
Severity: Critical
Advisory: GHSA-x2pc-fqrw-hc7f
CVE: CVE-2022-31506
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2022-07-12
Source: https://github.com/advisories/GHSA-x2pc-fqrw-hc7f
Type: github-advisory

## Affected
- PyPI: `opendiamond` — affected >=0

## Details
The cmusatyalab/opendiamond repository through 10.1.1 on GitHub allows absolute path traversal because the Flask send_file function is used unsafely. A patch is available on the `master` branch of the repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31506
- https://github.com/cmusatyalab/opendiamond/issues/52
- https://github.com/github/securitylab/issues/669#issuecomment-1117265726
- https://github.com/cmusatyalab/opendiamond/commit/398049c187ee644beabab44d6fece82251c1ea56
- https://github.com/cmusatyalab/opendiamond
