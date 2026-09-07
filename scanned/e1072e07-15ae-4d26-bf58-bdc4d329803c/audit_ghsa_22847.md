# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-pg99-mp4c-75g6
CVE: CVE-2020-0811
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pg99-mp4c-75g6
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.17

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge (HTML-based)L, aka Chakra Scripting Engine Memory Corruption Vulnerability. This CVE ID is unique from CVE-2020-0812.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-0811
- https://github.com/chakra-core/ChakraCore/pull/6385
- https://github.com/chakra-core/ChakraCore/pull/6385/commits/7e2c36091928d3f3aa58c01e1ef48bf6da777d09
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0811
