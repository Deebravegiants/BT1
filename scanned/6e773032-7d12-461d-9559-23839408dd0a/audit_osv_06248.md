# [M] Filter bypass in filter_var (FILTER_VALIDATE_URL)

## Summary
Severity: Medium
Advisory: BIT-libphp-2024-5458
Aliases: BIT-php-2024-5458, BIT-php-min-2024-5458, CVE-2024-5458, GHSA-w8qr-v226-r27w
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-5458
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.8

## Details
In PHP versions 8.1.* before 8.1.29, 8.2.* before 8.2.20, 8.3.* before 8.3.8, due to a code logic error, filtering functions such as filter_var when validating URLs (FILTER_VALIDATE_URL) for certain types of URLs the function will result in invalid user information (username + password part of URLs) being treated as valid user information. This may lead to the downstream code accepting invalid URLs as valid and parsing them incorrectly.

## References
- http://www.openwall.com/lists/oss-security/2024/06/07/1
- https://github.com/php/php-src/security/advisories/GHSA-w8qr-v226-r27w
- https://lists.debian.org/debian-lts-announce/2024/06/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PKGTQUOA2NTZ3RXN22CSAUJPIRUYRB4B/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/W45DBOH56NQDRTOM2DN2LNA2FZIMC3PK/
- https://nvd.nist.gov/vuln/detail/CVE-2024-5458
- https://security.netapp.com/advisory/ntap-20240726-0001/
- https://lists.debian.org/debian-lts-announce/2024/10/msg00011.html
