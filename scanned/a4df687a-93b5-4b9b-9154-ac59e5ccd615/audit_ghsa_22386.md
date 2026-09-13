# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-h5hw-qrrw-vfxg
CVE: CVE-2018-0954
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h5hw-qrrw-vfxg
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.4

## Details
A remote code execution vulnerability exists in the way the scripting engine handles objects in memory in Microsoft browsers, aka "Scripting Engine Memory Corruption Vulnerability." This affects Internet Explorer 9, ChakraCore, Internet Explorer 11, Microsoft Edge, Internet Explorer 10. This CVE ID is unique from CVE-2018-0945, CVE-2018-0946, CVE-2018-0951, CVE-2018-0953, CVE-2018-0955, CVE-2018-1022, CVE-2018-8114, CVE-2018-8122, CVE-2018-8128, CVE-2018-8137, CVE-2018-8139.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0954
- https://github.com/chakra-core/ChakraCore/commit/51c46371c917e87bbde77d66abba088309d96a3f
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-0954
- https://web.archive.org/web/20210124164423/http://www.securityfocus.com/bid/103991
- https://web.archive.org/web/20211204185256/http://www.securitytracker.com/id/1040844
