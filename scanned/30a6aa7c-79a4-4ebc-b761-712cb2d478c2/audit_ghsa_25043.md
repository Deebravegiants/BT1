# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-5q2v-52gc-4w7p
CVE: CVE-2018-0925
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5q2v-52gc-4w7p
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.2

## Details
ChakraCore allows remote code execution, due to how the ChakraCore scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability". This CVE ID is unique from CVE-2018-0876, CVE-2018-0889, CVE-2018-0893, and CVE-2018-0935.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0925
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-0925
- https://web.archive.org/web/20210124144841/http://www.securityfocus.com/bid/103287
