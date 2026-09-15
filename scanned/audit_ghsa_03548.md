# [H] Out-of-bounds write

## Summary
Severity: High
Advisory: GHSA-vw2g-5827-m9fp
CVE: CVE-2019-1308
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-vw2g-5827-m9fp
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.14

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka 'Chakra Scripting Engine Memory Corruption Vulnerability'. This CVE ID is unique from CVE-2019-1307, CVE-2019-1335, CVE-2019-1366.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1308
- https://github.com/chakra-core/ChakraCore/commit/64376deca69126c2bb05cd87bd5c073aedaf5f9c
- https://github.com/chakra-core/ChakraCore/commit/cc871514deeaeaedb5b757c2ca8cd4ab9abccb5d
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1308
