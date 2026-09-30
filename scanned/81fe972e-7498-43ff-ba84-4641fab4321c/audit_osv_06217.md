# [H] Null Dereference in SoapClient

## Summary
Severity: High
Advisory: BIT-libphp-2021-21702
Aliases: BIT-php-2021-21702, BIT-php-min-2021-21702, CVE-2021-21702
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2021-21702
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.0.0 <8.0.2

## Details
In PHP versions 7.3.x below 7.3.27, 7.4.x below 7.4.15 and 8.0.x below 8.0.2, when using SOAP extension to connect to a SOAP server, a malicious SOAP server could return malformed XML data as a response that would cause PHP to access a null pointer and thus cause a crash.

## References
- https://bugs.php.net/bug.php?id=80672
- https://lists.debian.org/debian-lts-announce/2021/07/msg00008.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-21702
- https://security.gentoo.org/glsa/202105-23
- https://security.netapp.com/advisory/ntap-20210312-0005/
- https://www.debian.org/security/2021/dsa-4856
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.tenable.com/security/tns-2021-14
