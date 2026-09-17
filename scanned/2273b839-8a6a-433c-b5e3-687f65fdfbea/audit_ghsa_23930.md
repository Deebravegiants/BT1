# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-jr84-p554-62pm
CVE: CVE-2020-0969
CWE: CWE-119, CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jr84-p554-62pm
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.18

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge (HTML-based), aka 'Chakra Scripting Engine Memory Corruption Vulnerability'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-0969
- https://github.com/chakra-core/ChakraCore/pull/6420
- https://github.com/chakra-core/ChakraCore/commit/cd58e8e6799ab11b02a1cfc30bac9a2171dabd4d
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0969
