# [H] High severity vulnerability that affects Microsoft.ChakraCore

## Summary
Severity: High
Advisory: GHSA-fv38-4c3m-25v8
CVE: CVE-2019-0592
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-04-09
Source: https://github.com/advisories/GHSA-fv38-4c3m-25v8
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.7

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka 'Chakra Scripting Engine Memory Corruption Vulnerability'. This CVE ID is unique from CVE-2019-0611.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0592
- https://github.com/advisories/GHSA-fv38-4c3m-25v8
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0592
