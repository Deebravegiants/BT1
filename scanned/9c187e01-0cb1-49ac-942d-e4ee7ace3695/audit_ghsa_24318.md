# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-5ppx-g65v-4vfv
CVE: CVE-2016-3296
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-5ppx-g65v-4vfv
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0

## Details
The Chakra JavaScript engine in Microsoft Edge allows remote attackers to execute arbitrary code via a crafted web site, aka "Scripting Engine Memory Corruption Vulnerability."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3296
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-096
- https://github.com/chakra-core/ChakraCore
- https://github.com/chakra-core/ChakraCore/wiki/Roadmap
- https://web.archive.org/web/20210116095719/http://www.securitytracker.com/id/1036569
- https://web.archive.org/web/20210123160236/http://www.securityfocus.com/bid/92283
