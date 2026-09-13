# [H] Out-of-bounds write

## Summary
Severity: High
Advisory: GHSA-9735-p6r2-2hgh
CVE: CVE-2019-0911
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-9735-p6r2-2hgh
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.9

## Details
A remote code execution vulnerability exists in the way the scripting engine handles objects in memory in Microsoft browsers, aka 'Scripting Engine Memory Corruption Vulnerability'. This CVE ID is unique from CVE-2019-0884, CVE-2019-0918.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0911
- https://github.com/chakra-core/ChakraCore/commit/a2deba5e1850782014a2a34678464b251e448337
- https://github.com/chakra-core/ChakraCore/commit/d797e3f00e34c12c8c0ae52f56344325439dccd7
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0911
