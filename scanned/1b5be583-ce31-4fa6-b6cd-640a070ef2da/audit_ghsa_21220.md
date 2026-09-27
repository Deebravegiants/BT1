# [C] Ganga allows absolute path traversal

## Summary
Severity: Critical
Advisory: GHSA-7488-6x3r-23w5
CVE: CVE-2022-31507
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2022-07-13
Source: https://github.com/advisories/GHSA-7488-6x3r-23w5
Type: github-advisory

## Affected
- PyPI: `ganga` — affected >=0 <8.5.10

## Details
The ganga-devs/ganga repository before 8.5.10 on GitHub allows absolute path traversal because the Flask `send_file` function is used unsafely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31507
- https://github.com/github/securitylab/issues/669#issuecomment-1117265726
- https://github.com/ganga-devs/ganga/commit/730e7aba192407d35eb37dd7938d49071124be8c
- https://github.com/advisories/GHSA-7488-6x3r-23w5
- https://github.com/ganga-devs/ganga
- https://github.com/ganga-devs/ganga/releases/tag/8.5.10
- https://github.com/pypa/advisory-database/tree/main/vulns/ganga/PYSEC-2022-225.yaml
