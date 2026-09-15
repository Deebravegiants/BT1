# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-6p7q-85qq-7c43
CVE: CVE-2017-0234
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6p7q-85qq-7c43
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.4.4

## Details
A remote code execution vulnerability exists in Microsoft Edge in the way that the Chakra JavaScript engine renders when handling objects in memory, aka "Scripting Engine Memory Corruption Vulnerability." This CVE ID is unique from CVE-2017-0224, CVE-2017-0228, CVE-2017-0229, CVE-2017-0230, CVE-2017-0235, CVE-2017-0236, and CVE-2017-0238.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0234
- https://github.com/chakra-core/ChakraCore/pull/2959
- https://github.com/chakra-core/ChakraCore/commit/a1345ad48064921e8eb45fa0297ce405a7df14d3
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-0234
- https://web.archive.org/web/20210124044042/http://www.securityfocus.com/bid/98229
- https://web.archive.org/web/20211019191652/http://www.securitytracker.com/id/1038431
