# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-38r7-rv5p-ggwq
CVE: CVE-2018-8359
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-38r7-rv5p-ggwq
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.10.2

## Details
A remote code execution vulnerability exists in the way that the ChakraCore scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability." This affects ChakraCore. This CVE ID is unique from CVE-2018-8353, CVE-2018-8355, CVE-2018-8371, CVE-2018-8372, CVE-2018-8373, CVE-2018-8385, CVE-2018-8389, CVE-2018-8390.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8359
- https://github.com/chakra-core/ChakraCore/pull/5596
- https://github.com/chakra-core/ChakraCore/commit/f8bdb180c4e9351f441e25dc818815d0c63af753
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8359
- https://web.archive.org/web/20210421013802/http://www.securityfocus.com/bid/104990
- https://web.archive.org/web/20211203061111/http://www.securitytracker.com/id/1041457
