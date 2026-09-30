# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-p97q-j98q-f98w
CVE: CVE-2018-8287
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p97q-j98q-f98w
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.10.1

## Details
A remote code execution vulnerability exists in the way the scripting engine handles objects in memory in Microsoft browsers, aka "Scripting Engine Memory Corruption Vulnerability." This affects ChakraCore, Internet Explorer 11, Microsoft Edge, Internet Explorer 10. This CVE ID is unique from CVE-2018-8242, CVE-2018-8283, CVE-2018-8288, CVE-2018-8291, CVE-2018-8296, CVE-2018-8298.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8287
- https://github.com/chakra-core/ChakraCore/pull/5444
- https://github.com/chakra-core/ChakraCore/commit/fa89a7031e75ca8b4a595765e897e8fc0d9fae76
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8287
- https://web.archive.org/web/20210125211352/http://www.securityfocus.com/bid/104634
- https://web.archive.org/web/20211202002348/http://www.securitytracker.com/id/1041256
- https://web.archive.org/web/20220120050525/http://www.securitytracker.com/id/1041258
