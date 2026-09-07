# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-ww6f-76ff-phhj
CVE: CVE-2016-3202
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-ww6f-76ff-phhj
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.2.0.0

## Details
The Microsoft (1) Chakra JavaScript, (2) JScript, and (3) VBScript engines, as used in Microsoft Internet Explorer 10 and 11 and Microsoft Edge, allow remote attackers to execute arbitrary code or cause a denial of service (memory corruption) via a crafted web site, aka "Scripting Engine Memory Corruption Vulnerability."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3202
- https://github.com/chakra-core/ChakraCore/commit/ff9067ebe9e1c92eff4e25da95070bfd5942da07
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-063
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-068
- https://github.com/chakra-core/ChakraCore
- https://web.archive.org/web/20211129115034/http://www.securitytracker.com/id/1036099
- https://web.archive.org/web/20211208124350/http://www.securitytracker.com/id/1036096
