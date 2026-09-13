# [H] Jerome Gamez Firebase Admin SDK for PHP Incorrect Access Control vulnerability

## Summary
Severity: High
Advisory: GHSA-4gjj-r7w8-42cq
CVE: CVE-2018-1000025
CWE: CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4gjj-r7w8-42cq
Type: github-advisory

## Affected
- Packagist: `kreait/firebase-php` — affected >=3.2.0 <3.8.1

## Details
Jerome Gamez Firebase Admin SDK for PHP version from 3.2.0 to 3.8.0 contains a Incorrect Access Control vulnerability in `src/Firebase/Auth/IdTokenVerifier.php` does not verify for token signature that can result in JWT with any email address and user ID could be forged from an actual token, or from thin air. This attack appear to be exploitable via Attacker would only need to know email address of the victim on most cases.. This vulnerability appears to have been fixed in 3.8.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000025
- https://github.com/kreait/firebase-php/pull/151
- https://github.com/FriendsOfPHP/security-advisories/blob/master/kreait/firebase-php/CVE-2018-1000025.yaml
- https://github.com/kreait/firebase-php
- https://github.com/kreait/firebase-php/releases/tag/3.8.1
