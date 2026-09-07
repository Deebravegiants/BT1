# [C] Missing Access Check in TYPO3 CMS

## Summary
Severity: Critical
Advisory: GHSA-gwfx-p7mr-f92v
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-gwfx-p7mr-f92v
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.25
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.8
- Packagist: `typo3/cms` — affected >=8.0.0 <8.1.1

## Details
Extbase request handling fails to implement a proper access check for requested controller/ action combinations, which makes it possible for an attacker to execute arbitrary Extbase actions by crafting a special request. To successfully exploit this vulnerability, an attacker must have access to at least one Extbase plugin or module action in a TYPO3 installation. The missing access check inevitably leads to information disclosure or remote code execution, depending on the action that an attacker is able to execute.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-05-24-1.yaml
- https://web.archive.org/web/20160606110438/https://typo3.org/teamssecuritysecurity-bulletins/security-bulletins-single-view/article/missing-access-check-in-typo3-cms
