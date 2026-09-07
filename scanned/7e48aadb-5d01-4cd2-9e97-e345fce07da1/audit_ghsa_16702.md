# [M] Passbolt Api E-mail HTML injection

## Summary
Severity: Medium
Advisory: GHSA-v86m-j5f7-ccwh
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-v86m-j5f7-ccwh
Type: github-advisory

## Affected
- Packagist: `passbolt/passbolt_api` — affected >=0 <2.7.0

## Details
Passbolt sends e-mail to users to warn them about different type of events such as the creation, modification or deletion of a password. Those e-mails may contain user-specified input, such as a password’s title or description.

Passbolt does not escape the user’s input properly, resulting in the user being able to inject HTML code in an e-mail.

An authenticated attacker could share a password containing an img HTML tag in its description with an other user to obtain information about their mail user-agent.

This vulnerability has a very low impact. Most MUA do not embed remote images to protect their users’ privacy.

## References
- https://github.com/passbolt/passbolt_api/commit/00f0ebe37d78815adee26d5e80cf2250fe878647
- https://github.com/FriendsOfPHP/security-advisories/blob/master/passbolt/passbolt_api/2019-02-11-3.yaml
- https://github.com/passbolt/passbolt_api
- https://www.passbolt.com/incidents/20190211_multiple_vulnerabilities
