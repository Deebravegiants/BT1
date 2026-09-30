# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-2589-r26x-mh8p
CVE: CVE-2018-8503
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2589-r26x-mh8p
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.2

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka "Chakra Scripting Engine Memory Corruption Vulnerability." This affects Microsoft Edge, ChakraCore. This CVE ID is unique from CVE-2018-8505, CVE-2018-8510, CVE-2018-8511, CVE-2018-8513.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8503
- https://github.com/chakra-core/ChakraCore/pull/5764
- https://github.com/chakra-core/ChakraCore/commit/062b4d9f42723ce7c2725f844cbf5431d52ca999
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8503
- https://web.archive.org/web/20210729123415/http://www.securityfocus.com/bid/105464
- https://web.archive.org/web/20210927074321/http://www.securitytracker.com/id/1041825
