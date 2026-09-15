# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-h6g3-73h7-chxp
CVE: CVE-2016-3260
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-h6g3-73h7-chxp
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.2.0.0

## Details
The Microsoft (1) JScript 9, (2) VBScript, and (3) Chakra JavaScript engines, as used in Microsoft Internet Explorer 11, Microsoft Edge, and other products, allow remote attackers to execute arbitrary code or cause a denial of service (memory corruption) via a crafted web site, aka "Scripting Engine Memory Corruption Vulnerability."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3260
- https://github.com/chakra-core/ChakraCore/pull/1291
- https://github.com/chakra-core/ChakraCore/commit/17f3d4a4852dcc9e48de7091685b1862afb9f307
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-084
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-085
- https://github.com/chakra-core/ChakraCore
- https://web.archive.org/web/20210123150650/http://www.securityfocus.com/bid/91580
- https://web.archive.org/web/20211202003833/http://www.securitytracker.com/id/1036283
