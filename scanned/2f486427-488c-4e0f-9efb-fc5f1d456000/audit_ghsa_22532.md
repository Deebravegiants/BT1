# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-7cc5-cqmx-9v7g
CVE: CVE-2018-8177
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7cc5-cqmx-9v7g
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.4

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka "Chakra Scripting Engine Memory Corruption Vulnerability." This affects ChakraCore. This CVE ID is unique from CVE-2018-0943, CVE-2018-8130, CVE-2018-8133, CVE-2018-8145.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8177
- https://github.com/chakra-core/ChakraCore/commit/eb4b00bcd61a56d5ac66f4155870cba3178d3273
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8177
- https://web.archive.org/web/20210124164218/http://www.securityfocus.com/bid/103967
