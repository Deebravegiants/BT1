# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-85j8-g29g-m326
CVE: CVE-2018-8371
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-85j8-g29g-m326
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.10.1

## Details
A remote code execution vulnerability exists in the way that the scripting engine handles objects in memory in Internet Explorer, aka "Scripting Engine Memory Corruption Vulnerability." This affects Internet Explorer 9, Internet Explorer 11, Internet Explorer 10. This CVE ID is unique from CVE-2018-8353, CVE-2018-8355, CVE-2018-8359, CVE-2018-8372, CVE-2018-8373, CVE-2018-8385, CVE-2018-8389, CVE-2018-8390.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8371
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8371
- https://web.archive.org/web/20210804005724/http://www.securityfocus.com/bid/105035
- https://web.archive.org/web/20211205174257/http://www.securitytracker.com/id/1041483
