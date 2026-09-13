# [H] Remote code execution in ChakraCore

## Summary
Severity: High
Advisory: GHSA-xxfr-jrgh-x392
CVE: CVE-2020-1172
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-xxfr-jrgh-x392
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.22

## Details
A remote code execution vulnerability exists in the way that the ChakraCore scripting engine handles objects in memory, aka 'Scripting Engine Memory Corruption Vulnerability'. This CVE ID is unique from CVE-2020-1057, CVE-2020-1180.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1172
- https://github.com/chakra-core/ChakraCore/pull/6500
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1172
