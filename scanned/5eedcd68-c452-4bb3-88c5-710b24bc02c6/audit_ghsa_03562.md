# [H] Out-of-bounds write 

## Summary
Severity: High
Advisory: GHSA-v89p-5hr2-4rh4
CVE: CVE-2019-1197
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-v89p-5hr2-4rh4
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.12

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka 'Chakra Scripting Engine Memory Corruption Vulnerability'. This CVE ID is unique from CVE-2019-1131, CVE-2019-1139, CVE-2019-1140, CVE-2019-1141, CVE-2019-1195, CVE-2019-1196.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1197
- https://github.com/chakra-core/ChakraCore/commit/6b1250b6ffea7006226dd937e52cf5b353fcfc15
- https://github.com/chakra-core/ChakraCore/commit/bf52b6cfa96d6395046d0aaf87396cd7ca13f6cb
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1197
