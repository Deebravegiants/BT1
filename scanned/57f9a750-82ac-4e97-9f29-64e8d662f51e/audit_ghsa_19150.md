# [M] AutoQueryable leaks sensitive information

## Summary
Severity: Medium
Advisory: GHSA-m4mm-534h-5cp5
CVE: CVE-2024-57716
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-20
Source: https://github.com/advisories/GHSA-m4mm-534h-5cp5
Type: github-advisory

## Affected
- NuGet: `AutoQueryable` — affected >=0

## Details
An issue in trenoncourt AutoQueryable v.1.7.0 allows a remote attacker to obtain sensitive information via the Unselectable function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57716
- https://github.com/pentesttoolscom/vulnerability-research/tree/master/CVE-2024-57716
- https://github.com/trenoncourt/AutoQueryable
