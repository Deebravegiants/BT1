# [H] Out-of-bounds write

## Summary
Severity: High
Advisory: GHSA-mg98-x2cm-4cpf
CVE: CVE-2019-1106
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-mg98-x2cm-4cpf
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.11

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka 'Chakra Scripting Engine Memory Corruption Vulnerability'. This CVE ID is unique from CVE-2019-1062, CVE-2019-1092, CVE-2019-1103, CVE-2019-1107.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1106
- https://github.com/chakra-core/ChakraCore/commit/362e96537af207be3ecf7fa32f338229ee1dcc46
- https://github.com/chakra-core/ChakraCore/commit/75162b7f2d8ac2b37d17564e9c979ba1bae707e8
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1106
