# [C] Use of Hard-coded Credentials in AgileConfig.Client

## Summary
Severity: Critical
Advisory: GHSA-mj5w-w588-j6xg
CVE: CVE-2022-35540
CWE: CWE-798
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-19
Source: https://github.com/advisories/GHSA-mj5w-w588-j6xg
Type: github-advisory

## Affected
- NuGet: `AgileConfig.Client` — affected >=0 <1.6.8

## Details
Hardcoded JWT Secret in AgileConfig <1.6.8 Server allows remote attackers to use the generated JWT token to gain administrator access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35540
- https://github.com/dotnetcore/AgileConfig/issues/91
- https://github.com/dotnetcore/AgileConfig
