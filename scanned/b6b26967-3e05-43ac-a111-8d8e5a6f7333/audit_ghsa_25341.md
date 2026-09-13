# [C] ChakraCore RCE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-8v2h-4jpm-3wfm
CVE: CVE-2017-8658
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-8v2h-4jpm-3wfm
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.6.1

## Details
A remote code execution vulnerability exists in the way that the Chakra JavaScript engine renders when handling objects in memory, aka "Scripting Engine Memory Corruption Vulnerability".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8658
- https://github.com/chakra-core/ChakraCore/pull/3509
- https://github.com/chakra-core/ChakraCore/commit/2500e1cdc12cb35af73d5c8c9b85656aba6bab4d
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-8658
- https://web.archive.org/web/20210124090857/http://www.securityfocus.com/bid/100036
