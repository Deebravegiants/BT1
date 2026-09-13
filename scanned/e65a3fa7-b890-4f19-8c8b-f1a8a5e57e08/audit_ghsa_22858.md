# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-g549-jfg6-98ch
CVE: CVE-2018-0994
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-g549-jfg6-98ch
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.3

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka "Chakra Scripting Engine Memory Corruption Vulnerability." This affects Microsoft Edge, ChakraCore. This CVE ID is unique from CVE-2018-0979, CVE-2018-0980, CVE-2018-0990, CVE-2018-0993, CVE-2018-0995, CVE-2018-1019.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0994
- https://github.com/chakra-core/ChakraCore/commit/0578ca55215d2eda74280e17c4b9bcc3c38dfd6a
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-0994
- https://web.archive.org/web/20210124154718/http://www.securityfocus.com/bid/103630
- https://web.archive.org/web/20211207123630/http://www.securitytracker.com/id/1040650
