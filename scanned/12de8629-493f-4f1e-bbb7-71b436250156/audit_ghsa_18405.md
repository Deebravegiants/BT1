# [M] Dagster vulnerable to Path Traversal attack through its /logs endpoint

## Summary
Severity: Medium
Advisory: GHSA-q93c-p2mw-p23f
CVE: CVE-2023-51232
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-07
Source: https://github.com/advisories/GHSA-q93c-p2mw-p23f
Type: github-advisory

## Affected
- PyPI: `dagster` — affected >=0 <1.5.11

## Details
Directory Traversal vulnerability in dagster-webserver Dagster thru 1.5.10 allows remote attackers to obtain sensitive information via crafted request to the /logs endpoint. This may be restricted to certain file names that start with a dot ('.').

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51232
- https://github.com/dagster-io/dagster/pull/18462
- https://github.com/dagster-io/dagster/commit/dbb064c2ddda74265b8174edd9775e1302ca6ba0
- https://github.com/dagster-io/dagster
