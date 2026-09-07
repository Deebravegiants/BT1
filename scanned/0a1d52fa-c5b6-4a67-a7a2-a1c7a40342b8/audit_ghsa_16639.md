# [H] Passbolt Api Remote code execution

## Summary
Severity: High
Advisory: GHSA-cv5c-2qv5-w2m2
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-cv5c-2qv5-w2m2
Type: github-advisory

## Affected
- Packagist: `passbolt/passbolt_api` — affected >=0 <2.7.0

## Details
Passbolt provides a way for system administrators to generate a PGP key for the server during installation. The wizard requests a username, an e-mail address and an optional comment. No escaping or verification is done by Passbolt, effectively allowing a user to inject bash code.

The impact is very high, but the probability is very low given that this vulnerability can only be exploited during Passbolt’s installation stage.

## References
- https://github.com/passbolt/passbolt_api/commit/be84671676ebac43d49e326a14f1afe259777611
- https://github.com/FriendsOfPHP/security-advisories/blob/master/passbolt/passbolt_api/2019-02-11-1.yaml
- https://github.com/passbolt/passbolt_api
- https://www.passbolt.com/incidents/20190211_multiple_vulnerabilities
