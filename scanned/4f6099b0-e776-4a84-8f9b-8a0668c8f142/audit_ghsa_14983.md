# [M] Privilege Escalation in TYPO3 Neos

## Summary
Severity: Medium
Advisory: GHSA-wr3c-6c22-m9v6
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-wr3c-6c22-m9v6
Type: github-advisory

## Affected
- Packagist: `typo3/neos` — affected >=1.1.0 <1.1.3
- Packagist: `typo3/neos` — affected >=1.2.0 <1.2.3

## Details
It has been discovered that TYPO3 Neos is vulnerable to Privilege Escalation. Logged in editors could access, create and modify content nodes that exist in the workspace of other editors.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/neos/2015-03-28.yaml
- https://www.neos.io/blog/neos-sa-2015-001.html
