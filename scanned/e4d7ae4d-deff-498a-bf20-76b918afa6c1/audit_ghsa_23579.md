# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-wjmf-6x7g-xq67
CVE: CVE-2018-1022
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wjmf-6x7g-xq67
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.4

## Details
A remote code execution vulnerability exists in the way the scripting engine handles objects in memory in Microsoft browsers, aka "Scripting Engine Memory Corruption Vulnerability." This affects ChakraCore, Internet Explorer 11, Microsoft Edge. This CVE ID is unique from CVE-2018-0945, CVE-2018-0946, CVE-2018-0951, CVE-2018-0953, CVE-2018-0954, CVE-2018-0955, CVE-2018-8114, CVE-2018-8122, CVE-2018-8128, CVE-2018-8137, CVE-2018-8139.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1022
- https://github.com/chakra-core/ChakraCore/commit/28928cba24968ed11022608f466c4ccc3470e64d
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-1022
- https://web.archive.org/web/20210124164250/http://www.securityfocus.com/bid/103978
- https://web.archive.org/web/20211204185256/http://www.securitytracker.com/id/1040844
