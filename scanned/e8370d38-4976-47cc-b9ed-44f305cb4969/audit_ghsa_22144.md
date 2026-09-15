# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-6xmv-mx7q-789r
CVE: CVE-2018-8456
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6xmv-mx7q-789r
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.1

## Details
A remote code execution vulnerability exists in the way that the ChakraCore scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability." This affects Microsoft Edge, ChakraCore. This CVE ID is unique from CVE-2018-8354, CVE-2018-8391, CVE-2018-8457, CVE-2018-8459.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8456
- https://github.com/chakra-core/ChakraCore/pull/5688
- https://github.com/chakra-core/ChakraCore/commit/98360625854f84262ce8de59a7f57496393281f3
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8456
- https://web.archive.org/web/20210124202635/http://www.securityfocus.com/bid/105227
- https://web.archive.org/web/20210517133345/http://www.securitytracker.com/id/1041623
