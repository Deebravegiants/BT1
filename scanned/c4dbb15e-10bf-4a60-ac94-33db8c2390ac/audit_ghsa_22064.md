# [C] ChakraCore RCE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-fw42-4mq4-4qpq
CVE: CVE-2018-8500
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fw42-4mq4-4qpq
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.2

## Details
A remote code execution vulnerability exists in the way that the ChakraCore scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability." This affects ChakraCore.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8500
- https://github.com/chakra-core/ChakraCore/pull/5764
- https://github.com/chakra-core/ChakraCore/commit/cd84a0b85b4b2bcf1653c7bfd5426bbc72b2b216
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8500
- https://web.archive.org/web/20210124210846/http://www.securityfocus.com/bid/105463
