# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-g3m9-qrfj-xw4g
CVE: CVE-2020-1073
CWE: CWE-119, CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g3m9-qrfj-xw4g
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.20

## Details
A remote code execution vulnerability exists in the way that the ChakraCore scripting engine handles objects in memory, aka 'Scripting Engine Memory Corruption Vulnerability'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1073
- https://github.com/chakra-core/ChakraCore/pull/6464
- https://github.com/chakra-core/ChakraCore/commit/82d3c4556a3cba13f0115fc98a91263b15fa6d07
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1073
