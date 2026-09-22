# [H] Regular Expression Denial of Service in System.Text.RegularExpressions

## Summary
Severity: High
Advisory: GHSA-cmhx-cq75-c4mj
CVE: CVE-2019-0820
CWE: CWE-1333, CWE-400
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-04
Source: https://github.com/advisories/GHSA-cmhx-cq75-c4mj
Type: github-advisory

## Affected
- NuGet: `System.Text.RegularExpressions` — affected >=4.3.0 <4.3.1

## Details
A denial of service vulnerability exists when .NET Framework and .NET Core improperly process RegEx strings, aka '.NET Framework and .NET Core Denial of Service Vulnerability'. This CVE ID is unique from CVE-2019-0980, CVE-2019-0981.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0820
- https://access.redhat.com/errata/RHSA-2019:1259
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0820
