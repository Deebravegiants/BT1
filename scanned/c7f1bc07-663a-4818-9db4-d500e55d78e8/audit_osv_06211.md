# [M] Use-of-uninitialized-value in exif

## Summary
Severity: Medium
Advisory: BIT-libphp-2020-7064
Aliases: BIT-php-2020-7064, BIT-php-min-2020-7064, CVE-2020-7064
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2020-7064
Type: osv

## Affected
- Bitnami: `libphp` — affected >=7.4.0 <7.4.4

## Details
In PHP versions 7.2.x below 7.2.9, 7.3.x below 7.3.16 and 7.4.x below 7.4.4, while parsing EXIF data with exif_read_data() function, it is possible for malicious data to cause PHP to read one byte of uninitialized memory. This could potentially lead to information disclosure or crash.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00025.html
- https://bugs.php.net/bug.php?id=79282
- https://lists.debian.org/debian-lts-announce/2020/04/msg00021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-7064
- https://security.netapp.com/advisory/ntap-20200403-0001/
- https://usn.ubuntu.com/4330-1/
- https://usn.ubuntu.com/4330-2/
- https://www.debian.org/security/2020/dsa-4717
- https://www.debian.org/security/2020/dsa-4719
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.tenable.com/security/tns-2021-14
