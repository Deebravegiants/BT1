# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-7gjv-9m33-chg8
CVE: CVE-2018-0858
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7gjv-9m33-chg8
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.1

## Details
ChakraCore allows remote code execution, due to how the ChakraCore scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability". This CVE ID is unique from CVE-2018-0834, CVE-2018-0835, CVE-2018-0836, CVE-2018-0837, CVE-2018-0838, CVE-2018-0840, CVE-2018-0856, CVE-2018-0857, CVE-2018-0859, CVE-2018-0860, CVE-2018-0861, and CVE-2018-0866.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0858
- https://github.com/chakra-core/ChakraCore/commit/972009a89e51c69971b80b1f5394886b304f880a
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-0858
- https://web.archive.org/web/20210124135655/http://www.securityfocus.com/bid/102865
- https://web.archive.org/web/20211208072939/http://www.securitytracker.com/id/1040372
