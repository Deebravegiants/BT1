# [M] Privilege Escalation in TYPO3 CMS

## Summary
Severity: Medium
Advisory: GHSA-v5jp-4h2p-j2p4
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-v5jp-4h2p-j2p4
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.20
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.5
- Packagist: `typo3/cms` — affected >=8.0.0 <8.0.1

## Details
The workspace/ version preview link created by a privileged (backend) user could be abused to obtain certain editing permission, if the admin panel is configured to be shown. A valid preview link is required to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-04-12-4.yaml
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2016-012
