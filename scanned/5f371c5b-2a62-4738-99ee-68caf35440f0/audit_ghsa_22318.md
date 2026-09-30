# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-6x4f-5v4h-r29j
CVE: CVE-2019-0567
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6x4f-5v4h-r29j
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.5

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka "Chakra Scripting Engine Memory Corruption Vulnerability." This affects Microsoft Edge, ChakraCore. This CVE ID is unique from CVE-2019-0539, CVE-2019-0568.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0567
- https://github.com/chakra-core/ChakraCore/commit/788f17b0ce06ea84553b123c174d1ff7052112a0
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0567
- https://web.archive.org/web/20210124231426/http://www.securityfocus.com/bid/106418
- https://www.exploit-db.com/exploits/46203
