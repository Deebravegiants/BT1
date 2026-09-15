# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-p94c-r74j-43qg
CVE: CVE-2016-3350
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-p94c-r74j-43qg
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.2.1

## Details
The Chakra JavaScript engine in Microsoft Edge allows remote attackers to execute arbitrary code or cause a denial of service (memory corruption) via a crafted web site, aka "Scripting Engine Memory Corruption Vulnerability," a different vulnerability than CVE-2016-3377.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3350
- https://github.com/chakra-core/ChakraCore/commit/24c4d7df8199b27d360323ce3be1d7959fd918eb
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-105
- https://github.com/chakra-core/ChakraCore
- https://web.archive.org/web/20210123044830/http://www.securitytracker.com/id/1036789
- https://web.archive.org/web/20210123164600/http://www.securityfocus.com/bid/92793
