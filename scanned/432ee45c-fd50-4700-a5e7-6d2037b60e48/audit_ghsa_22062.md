# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-f8f9-q5hg-9c7q
CVE: CVE-2017-11801
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-f8f9-q5hg-9c7q
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.7.3

## Details
ChakraCore allows an attacker to execute arbitrary code in the context of the current user, due to how the ChakraCore scripting engine handles objects in memory, aka "Scripting Engine Information Disclosure Vulnerability". This CVE ID is unique from CVE-2017-11792, CVE-2017-11793, CVE-2017-11796, CVE-2017-11797, CVE-2017-11798, CVE-2017-11799, CVE-2017-11800, CVE-2017-11802, CVE-2017-11804, CVE-2017-11805, CVE-2017-11806, CVE-2017-11807, CVE-2017-11808, CVE-2017-11809, CVE-2017-11810, CVE-2017-11811, CVE-2017-11812, and CVE-2017-11821.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11801
- https://github.com/chakra-core/ChakraCore/pull/3917
- https://github.com/chakra-core/ChakraCore/commit/7b936e208e6a5f8dea84340760205d25c0efdf43
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11801
- https://web.archive.org/web/20210124110147/http://www.securityfocus.com/bid/101146
