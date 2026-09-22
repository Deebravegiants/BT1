# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-px6p-jxwr-27mc
CVE: CVE-2017-11805
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-px6p-jxwr-27mc
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.7.3

## Details
ChakraCore and Microsoft Edge in Microsoft Windows 10 1703 allows an attacker to execute arbitrary code in the context of the current user, due to how the scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability". This CVE ID is unique from CVE-2017-11792, CVE-2017-11793, CVE-2017-11796, CVE-2017-11797, CVE-2017-11798, CVE-2017-11799, CVE-2017-11800, CVE-2017-11801, CVE-2017-11802, CVE-2017-11804, CVE-2017-11806, CVE-2017-11807, CVE-2017-11808, CVE-2017-11809, CVE-2017-11810, CVE-2017-11811, CVE-2017-11812, and CVE-2017-11821.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11805
- https://github.com/chakra-core/ChakraCore/pull/3917
- https://github.com/chakra-core/ChakraCore/commit/a9ea5c9365a6c7957df2afb41f970da87066ec2a
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11805
- https://web.archive.org/web/20210125203400/http://www.securityfocus.com/bid/101132
- https://web.archive.org/web/20210723180751/http://www.securitytracker.com/id/1039529
