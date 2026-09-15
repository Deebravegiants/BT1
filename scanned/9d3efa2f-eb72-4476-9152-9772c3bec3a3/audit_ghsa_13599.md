# [H] Yamcs Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-w4m2-qmh3-2g8f
CVE: CVE-2023-45277
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-w4m2-qmh3-2g8f
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs` — affected >=0 <5.8.7

## Details
Yamcs 5.8.6 is vulnerable to directory traversal (issue 1 of 2). The vulnerability is in the storage functionality of the API and allows one to escape the base directory of the buckets, freely navigate system directories, and read arbitrary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45277
- https://github.com/yamcs/yamcs
- https://github.com/yamcs/yamcs/compare/yamcs-5.8.6...yamcs-5.8.7
- https://www.linkedin.com/pulse/yamcs-vulnerability-assessment-visionspace-technologies
