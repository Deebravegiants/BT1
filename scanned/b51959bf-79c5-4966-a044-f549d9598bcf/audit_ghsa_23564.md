# [C] ChakraCore RCE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-448h-7hmp-99fg
CVE: CVE-2017-0223
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-448h-7hmp-99fg
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.4.4

## Details
A remote code execution vulnerability exists in Microsoft Chakra Core in the way JavaScript engines render when handling objects in memory. aka "Scripting Engine Memory Corruption Vulnerability". This vulnerability is unique from CVE-2017-0252.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0223
- https://github.com/Microsoft/ChakraCore/pull/2959
- https://github.com/chakra-core/ChakraCore/pull/2959
- https://github.com/chakra-core/ChakraCore/commit/f74773f4520adff6b70a7d445417aa9769f61fa6
- https://github.com/chakra-core/ChakraCore
- https://web.archive.org/web/20210124184849/http://www.securitytracker.com/id/1038425
