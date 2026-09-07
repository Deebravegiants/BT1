# [H] silverstripe/userforms vulnerable to remote code execution via userforms email subject

## Summary
Severity: High
Advisory: GHSA-g8wr-r2v2-vqc6
CVE: CVE-2026-54721
CWE: CWE-20, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-27
Source: https://github.com/advisories/GHSA-g8wr-r2v2-vqc6
Type: github-advisory

## Affected
- Packagist: `silverstripe/userforms` — affected >=0 <6.4.9
- Packagist: `silverstripe/userforms` — affected >=7.0.0 <7.0.7
- Packagist: `silverstripe/userforms` — affected >=7.1.0 <7.1.1

## Details
### Impact
The userform email subject field in the CMS is vulnerable to a specially crafted payload being used to run arbitrary code on the server.

### Reported by
Jack Wallace from Bastion Security

## References
- https://github.com/silverstripe/silverstripe-userforms/security/advisories/GHSA-g8wr-r2v2-vqc6
- https://github.com/silverstripe/silverstripe-userforms/pull/1441
- https://github.com/silverstripe/silverstripe-userforms/pull/1442
- https://github.com/silverstripe/silverstripe-userforms/commit/23c069866900c19b499bfa997d1e251e97491702
- https://github.com/silverstripe/silverstripe-userforms/commit/c55494ad7c717b199a3c1663b43a54db5d95604c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/userforms/CVE-2026-54721.yaml
- https://github.com/silverstripe/silverstripe-userforms
- https://github.com/silverstripe/silverstripe-userforms/releases/tag/6.4.9
- https://github.com/silverstripe/silverstripe-userforms/releases/tag/7.0.7
- https://github.com/silverstripe/silverstripe-userforms/releases/tag/7.1.1
- https://www.silverstripe.org/download/security-releases/cve-2026-54721
