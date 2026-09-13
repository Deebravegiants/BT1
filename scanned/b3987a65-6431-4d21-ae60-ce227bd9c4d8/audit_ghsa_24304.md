# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-68cp-h96v-gg3x
CVE: CVE-2017-0224
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-68cp-h96v-gg3x
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.4.4

## Details
A remote code execution vulnerability exists in the way JavaScript engines render when handling objects in memory in Microsoft Edge, aka "Scripting Engine Memory Corruption Vulnerability." This CVE ID is unique from CVE-2017-0228, CVE-2017-0229, CVE-2017-0230, CVE-2017-0234, CVE-2017-0235, CVE-2017-0236, and CVE-2017-0238.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0224
- https://github.com/chakra-core/ChakraCore/pull/2959
- https://github.com/chakra-core/ChakraCore/commit/f022afb8246acc98e74a887bb655ac512caf6e72
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-0224
- https://web.archive.org/web/20210124043822/http://www.securityfocus.com/bid/98214
