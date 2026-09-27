# [H] ChakraCore Memory Corruption Vulnerability

## Summary
Severity: High
Advisory: GHSA-5rq3-9wc9-m9c3
CVE: CVE-2019-0829
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5rq3-9wc9-m9c3
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.8

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka 'Chakra Scripting Engine Memory Corruption Vulnerability'. This CVE ID is unique from CVE-2019-0806, CVE-2019-0810, CVE-2019-0812, CVE-2019-0860, CVE-2019-0861.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0829
- https://github.com/chakra-core/ChakraCore/pull/6087
- https://github.com/chakra-core/ChakraCore/commit/b03a96112fb05158a040caba88919cd70648f09f
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0829
