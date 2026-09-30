# [M] Incorrect URL validation in FILTER_VALIDATE_URL

## Summary
Severity: Medium
Advisory: BIT-libphp-2021-21705
Aliases: BIT-php-2021-21705, BIT-php-min-2021-21705, CVE-2021-21705
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2021-21705
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.0.0 <8.0.8

## Details
In PHP versions 7.3.x below 7.3.29, 7.4.x below 7.4.21 and 8.0.x below 8.0.8, when using URL validation functionality via filter_var() function with FILTER_VALIDATE_URL parameter, an URL with invalid password field can be accepted as valid. This can lead to the code incorrectly parsing the URL and potentially leading to other security implications - like contacting a wrong server or making a wrong access decision.

## References
- https://bugs.php.net/bug.php?id=81122
- https://nvd.nist.gov/vuln/detail/CVE-2021-21705
- https://security.gentoo.org/glsa/202209-20
- https://security.netapp.com/advisory/ntap-20211029-0006/
- https://www.oracle.com/security-alerts/cpujan2022.html
