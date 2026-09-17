# [C] Firebase PHP-JWT key/algorithm type confusion

## Summary
Severity: Critical
Advisory: GHSA-8xf4-w7qw-pjjw
CVE: CVE-2021-46743
CWE: CWE-347, CWE-843
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-8xf4-w7qw-pjjw
Type: github-advisory

## Affected
- Packagist: `firebase/php-jwt` — affected >=0 <6.0.0

## Details
In Firebase PHP-JWT before 6.0.0, an algorithm-confusion issue (e.g., RS256 / HS256) exists via the kid (aka Key ID) header, when multiple types of keys are loaded in a key ring. This allows an attacker to forge tokens that validate under the incorrect key. NOTE: this provides a straightforward way to use the PHP-JWT library unsafely, but might not be considered a vulnerability in the library itself.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46743
- https://github.com/firebase/php-jwt/issues/351
- https://github.com/FriendsOfPHP/security-advisories/blob/master/firebase/php-jwt/CVE-2021-46743.yaml
- https://github.com/firebase/php-jwt
- https://github.com/firebase/php-jwt/releases/tag/v6.0.0
