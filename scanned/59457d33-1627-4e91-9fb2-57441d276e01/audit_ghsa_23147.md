# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-q6mv-8vh9-4ggj
CVE: CVE-2016-3248
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-q6mv-8vh9-4ggj
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0

## Details
The Microsoft (1) JScript 9, (2) VBScript, and (3) Chakra JavaScript engines, as used in Microsoft Internet Explorer 9 through 11, Microsoft Edge, and other products, allow remote attackers to execute arbitrary code or cause a denial of service (memory corruption) via a crafted web site, aka "Scripting Engine Memory Corruption Vulnerability," a different vulnerability than CVE-2016-3259.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3248
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-084
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-085
- https://github.com/chakra-core/ChakraCore
- https://github.com/chakra-core/ChakraCore/wiki/Roadmap
- https://web.archive.org/web/20210125172707/http://www.securityfocus.com/bid/91578
- https://web.archive.org/web/20211202003833/http://www.securitytracker.com/id/1036283
