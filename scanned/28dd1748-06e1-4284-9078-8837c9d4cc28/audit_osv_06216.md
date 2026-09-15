# [M] FILTER_VALIDATE_URL accepts URLs with invalid userinfo

## Summary
Severity: Medium
Advisory: BIT-libphp-2020-7071
Aliases: BIT-php-2020-7071, BIT-php-min-2020-7071, CVE-2020-7071
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2020-7071
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.0.0 <8.0.1

## Details
In PHP versions 7.3.x below 7.3.26, 7.4.x below 7.4.14 and 8.0.0, when validating URL with functions like filter_var($url, FILTER_VALIDATE_URL), PHP will accept an URL with invalid password as valid URL. This may lead to functions that rely on URL being valid to mis-parse the URL and produce wrong data as components of the URL.

## References
- https://bugs.php.net/bug.php?id=77423
- https://lists.debian.org/debian-lts-announce/2021/07/msg00008.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-7071
- https://security.gentoo.org/glsa/202105-23
- https://security.netapp.com/advisory/ntap-20210312-0005/
- https://www.debian.org/security/2021/dsa-4856
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.tenable.com/security/tns-2021-14
