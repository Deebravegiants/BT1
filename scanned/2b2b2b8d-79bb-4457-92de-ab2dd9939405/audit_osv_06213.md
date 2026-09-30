# [H] OOB Read in urldecode()

## Summary
Severity: High
Advisory: BIT-libphp-2020-7067
Aliases: BIT-php-2020-7067, BIT-php-min-2020-7067, CVE-2020-7067
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2020-7067
Type: osv

## Affected
- Bitnami: `libphp` — affected >=7.4.0 <7.4.5

## Details
In PHP versions 7.2.x below 7.2.30, 7.3.x below 7.3.17 and 7.4.x below 7.4.5, if PHP is compiled with EBCDIC support (uncommon), urldecode() function can be made to access locations past the allocated memory, due to erroneously using signed numbers as array indexes.

## References
- https://bugs.php.net/bug.php?id=79465
- https://nvd.nist.gov/vuln/detail/CVE-2020-7067
- https://security.netapp.com/advisory/ntap-20200504-0001/
- https://www.debian.org/security/2020/dsa-4717
- https://www.debian.org/security/2020/dsa-4719
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.tenable.com/security/tns-2021-14
