# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-6g23-fww6-rfrj
CVE: CVE-2018-8354
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6g23-fww6-rfrj
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.1

## Details
A remote code execution vulnerability exists in the way that the scripting engine handles objects in memory in Microsoft Edge, aka "Scripting Engine Memory Corruption Vulnerability." This affects Microsoft Edge, ChakraCore. This CVE ID is unique from CVE-2018-8391, CVE-2018-8456, CVE-2018-8457, CVE-2018-8459.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8354
- https://github.com/chakra-core/ChakraCore/pull/5688
- https://github.com/chakra-core/ChakraCore/commit/5192cdc08a030a580ba15d1d9aa50f81a6d92211
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8354
- https://web.archive.org/web/20210124202704/http://www.securityfocus.com/bid/105232
- https://web.archive.org/web/20210517133345/http://www.securitytracker.com/id/1041623
