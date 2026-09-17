# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-67f9-qmg7-fmcq
CVE: CVE-2018-0874
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-67f9-qmg7-fmcq
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.2

## Details
ChakraCore and Microsoft Edge in Microsoft Windows 10 Gold, 1511, 1607, 1703, 1709, and Windows Server 2016 allows remote code execution, due to how the Chakra scripting engine handles objects in memory, aka "Chakra Scripting Engine Memory Corruption Vulnerability". This CVE ID is unique from CVE-2018-0872, CVE-2018-0873, CVE-2018-0930, CVE-2018-0931, CVE-2018-0933, CVE-2018-0934, CVE-2018-0936, and CVE-2018-0937.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0874
- https://github.com/chakra-core/ChakraCore/commit/7087c314a67631a0a3094bc2f741991ee10f5b5a
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-0874
- https://web.archive.org/web/20201021051922/http://www.securitytracker.com/id/1040507
- https://web.archive.org/web/20210124144659/http://www.securityfocus.com/bid/103269
