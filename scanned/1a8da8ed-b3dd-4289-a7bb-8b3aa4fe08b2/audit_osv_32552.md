# [H] NamelessMC Vulnerable to SQL Injections in /user/messaging and /panel/users/reports Pages

## Summary
Severity: High
Advisory: CVE-2025-32389
Aliases: GHSA-5984-mhcp-cq2x
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-32389
Type: osv

## Details
NamelessMC is a free, easy to use & powerful website software for Minecraft servers. Prior to version 2.1.4, NamelessMC is vulnerable to SQL injection by providing an unexpected square bracket GET parameter syntax. Square bracket GET parameter syntax refers to the structure `?param[0]=a&param[1]=b&param[2]=c` utilized by PHP, which is parsed by PHP as `$_GET['param']` being of type array. This issue has been patched in version 2.1.4.

## References
- https://github.com/NamelessMC/Nameless/releases/tag/v2.1.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32389.json
- https://github.com/NamelessMC/Nameless/security/advisories/GHSA-5984-mhcp-cq2x
- https://nvd.nist.gov/vuln/detail/CVE-2025-32389
- https://github.com/NamelessMC/Nameless/commit/02c81c7c45b98fad1ebe3bc085efae18aec4566f
