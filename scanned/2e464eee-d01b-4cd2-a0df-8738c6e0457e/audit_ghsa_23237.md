# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-399v-jg88-3gx6
CVE: CVE-2018-0856
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-399v-jg88-3gx6
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.1

## Details
Microsoft Edge and ChakraCore in Microsoft Windows 10 1703 and 1709 allows remote code execution, due to how the scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability". This CVE ID is unique from CVE-2018-0834, CVE-2018-0835, CVE-2018-0836, CVE-2018-0837, CVE-2018-0838, CVE-2018-0840, CVE-2018-0857, CVE-2018-0858, CVE-2018-0859, CVE-2018-0860, CVE-2018-0861, and CVE-2018-0866.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0856
- https://github.com/chakra-core/ChakraCore/commit/385af842bce4f94ddef98553a81f8ea99c7e2dcf
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-0856
- https://web.archive.org/web/20210125205300/http://www.securityfocus.com/bid/102880
- https://web.archive.org/web/20211208072939/http://www.securitytracker.com/id/1040372
