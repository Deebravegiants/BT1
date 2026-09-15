# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-gxcf-6h72-8gxf
CVE: CVE-2018-8367
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gxcf-6h72-8gxf
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.1

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka "Chakra Scripting Engine Memory Corruption Vulnerability." This affects Microsoft Edge, ChakraCore. This CVE ID is unique from CVE-2018-8465, CVE-2018-8466, CVE-2018-8467.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8367
- https://github.com/chakra-core/ChakraCore/pull/5688
- https://github.com/chakra-core/ChakraCore/commit/dd5b2e75e7aebe67b5185383080c0648f5353ea0
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8367
- https://web.archive.org/web/20210125212221/http://www.securityfocus.com/bid/105245
- https://web.archive.org/web/20210517133345/http://www.securitytracker.com/id/1041623
