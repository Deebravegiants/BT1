# [H] Out-of-bounds write in ChakraCore

## Summary
Severity: High
Advisory: GHSA-pfrg-w49c-8432
CVE: CVE-2020-0768
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-pfrg-w49c-8432
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.17

## Details
A remote code execution vulnerability exists in the way the scripting engine handles objects in memory in Microsoft browsers, aka 'Scripting Engine Memory Corruption Vulnerability'. This CVE ID is unique from CVE-2020-0823, CVE-2020-0825, CVE-2020-0826, CVE-2020-0827, CVE-2020-0828, CVE-2020-0829, CVE-2020-0830, CVE-2020-0831, CVE-2020-0832, CVE-2020-0833, CVE-2020-0848.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-0768
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0768
