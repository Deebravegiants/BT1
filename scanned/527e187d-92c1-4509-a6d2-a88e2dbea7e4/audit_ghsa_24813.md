# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-6v8r-83v3-rmrf
CVE: CVE-2018-0936
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6v8r-83v3-rmrf
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.2

## Details
ChakraCore and Microsoft Windows 10 1709 allow remote code execution, due to how the Chakra scripting engine handles objects in memory, aka "Chakra Scripting Engine Memory Corruption Vulnerability". This CVE ID is unique from CVE-2018-0872, CVE-2018-0873, CVE-2018-0874, CVE-2018-0930, CVE-2018-0931, CVE-2018-0933, CVE-2018-0934, and CVE-2018-0937.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0936
- https://github.com/chakra-core/ChakraCore/commit/64e761923df08a458291bca9933f922b167a8f0e
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-0936
- https://web.archive.org/web/20210124144704/http://www.securityfocus.com/bid/103270
- https://web.archive.org/web/20211026192005/http://www.securitytracker.com/id/1040507
