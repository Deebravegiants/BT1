# [H] Joomla RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-9m72-pw47-292w
CVE: CVE-2018-17856
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9m72-pw47-292w
Type: github-advisory

## Affected
- Packagist: `joomla/framework` — affected >=2.5.4 <3.8.13

## Details
An issue was discovered in Joomla! before 3.8.13. com_joomlaupdate allows the execution of arbitrary code. The default ACL config enabled the ability of Administrator-level users to access com_joomlaupdate and trigger code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17856
- https://developer.joomla.org/security-centre/752-20181002-core-inadequate-default-access-level-for-com-joomlaupdate.html
- https://github.com/joomla/joomla-cms
- https://web.archive.org/web/20210124211736/http://www.securityfocus.com/bid/105559
- https://web.archive.org/web/20211208125303/http://www.securitytracker.com/id/1041914
