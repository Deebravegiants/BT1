# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-frh8-wrx9-gc53
CVE: CVE-2018-8137
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-frh8-wrx9-gc53
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.4

## Details
A remote code execution vulnerability exists in the way that the scripting engine handles objects in memory in Microsoft Edge, aka "Scripting Engine Memory Corruption Vulnerability." This affects Microsoft Edge, ChakraCore. This CVE ID is unique from CVE-2018-0945, CVE-2018-0946, CVE-2018-0951, CVE-2018-0953, CVE-2018-0954, CVE-2018-0955, CVE-2018-1022, CVE-2018-8114, CVE-2018-8122, CVE-2018-8128, CVE-2018-8139.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8137
- https://github.com/chakra-core/ChakraCore/commit/6e362fe94bc4bba7c8b8c6f819c1bee94c51893c
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8137
- https://web.archive.org/web/20210124164218/http://www.securityfocus.com/bid/103967
- https://web.archive.org/web/20211204185256/http://www.securitytracker.com/id/1040844
