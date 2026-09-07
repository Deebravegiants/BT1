# [M] TYPO3 sf_register extension allows unauthorized assignment of frontend user groups

## Summary
Severity: Medium
Advisory: GHSA-v348-vr4q-fv9p
CVE: CVE-2026-46721
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-v348-vr4q-fv9p
Type: github-advisory

## Affected
- Packagist: `evoweb/sf-register` — affected >=14.0.0 <14.0.2
- Packagist: `evoweb/sf-register` — affected >=0 <13.2.4

## Details
The `create` and `edit` flows in the TYPO3 extension sf_register do not restrict which user properties may be submitted, and do not enforce access control on the frontend user group assignment. As a result, an attacker can assign an arbitrary frontend user group to a newly registered or edited account, gaining unauthorized access to content and functionality restricted to privileged frontend user groups.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46721
- https://github.com/FriendsOfPHP/security-advisories/blob/master/evoweb/sf-register/CVE-2026-46721.yaml
- https://github.com/evoWeb/sf_register
- https://typo3.org/security/advisory/typo3-ext-sa-2026-009
