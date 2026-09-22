# [C] Improper Authorization in modoboa

## Summary
Severity: Critical
Advisory: GHSA-67mg-gm8m-ph5r
CVE: CVE-2023-2227
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-04-21
Source: https://github.com/advisories/GHSA-67mg-gm8m-ph5r
Type: github-advisory

## Affected
- PyPI: `modoboa` — affected >=0 <2.1.0

## Details
In modoboa prior to 2.1.0, sending a GET request to the endpoint `/api/v2/parameters/core/` returns sensitive information without any authentication or authorization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2227
- https://github.com/modoboa/modoboa/commit/7bcd3f6eb264d4e3e01071c97c2bac51cdd6fe97
- https://github.com/modoboa/modoboa
- https://github.com/pypa/advisory-database/tree/main/vulns/modoboa/PYSEC-2023-35.yaml
- https://huntr.dev/bounties/351f9055-2008-4af0-b820-01ff66678bf3
