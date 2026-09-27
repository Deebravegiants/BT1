# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-67x3-36j7-pj4g
CVE: CVE-2018-8385
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-67x3-36j7-pj4g
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.10.2

## Details
A remote code execution vulnerability exists in the way the scripting engine handles objects in memory in Microsoft browsers, aka "Scripting Engine Memory Corruption Vulnerability." This affects Internet Explorer 9, ChakraCore, Internet Explorer 11, Microsoft Edge, Internet Explorer 10. This CVE ID is unique from CVE-2018-8353, CVE-2018-8355, CVE-2018-8359, CVE-2018-8371, CVE-2018-8372, CVE-2018-8373, CVE-2018-8389, CVE-2018-8390.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8385
- https://github.com/chakra-core/ChakraCore/pull/5596
- https://github.com/chakra-core/ChakraCore/commit/f00612bbc3657f1ec33a9e7d575c16a5489d06aa
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8385
- https://web.archive.org/web/20210124195607/http://www.securityfocus.com/bid/105039
- https://web.archive.org/web/20211203061111/http://www.securitytracker.com/id/1041457
