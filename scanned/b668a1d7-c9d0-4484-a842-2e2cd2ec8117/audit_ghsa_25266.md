# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-w4qx-vw2w-q566
CVE: CVE-2018-8243
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-w4qx-vw2w-q566
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.5

## Details
A remote code execution vulnerability exists in the way that the ChakraCore scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability." This affects ChakraCore. This CVE ID is unique from CVE-2018-8267.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8243
- https://github.com/chakra-core/ChakraCore/wiki/Roadmap#v185
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8243
- https://web.archive.org/web/20210124175604/http://www.securityfocus.com/bid/104403
