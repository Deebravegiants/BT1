# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-67xp-4726-4978
CVE: CVE-2020-0710
CWE: CWE-119, CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-67xp-4726-4978
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.16

## Details
A remote code execution vulnerability exists in the way that the ChakraCore scripting engine handles objects in memory, aka 'Scripting Engine Memory Corruption Vulnerability'. This CVE ID is unique from CVE-2020-0673, CVE-2020-0674, CVE-2020-0711, CVE-2020-0712, CVE-2020-0713, CVE-2020-0767.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-0710
- https://github.com/chakra-core/ChakraCore/pull/6375
- https://github.com/chakra-core/ChakraCore/pull/6375/commits/d89802674a591904c971f2d92b96b8f40839e7c7
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0710
