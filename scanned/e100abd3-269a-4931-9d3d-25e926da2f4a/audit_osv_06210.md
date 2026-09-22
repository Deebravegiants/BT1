# [M] Files added to tar with Phar::buildFromIterator have all-access permissions

## Summary
Severity: Medium
Advisory: BIT-libphp-2020-7063
Aliases: BIT-php-2020-7063, BIT-php-min-2020-7063, CVE-2020-7063
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2020-7063
Type: osv

## Affected
- Bitnami: `libphp` — affected >=7.4.0 <7.4.3

## Details
In PHP versions 7.2.x below 7.2.28, 7.3.x below 7.3.15 and 7.4.x below 7.4.3, when creating PHAR archive using PharData::buildFromIterator() function, the files are added with default permissions (0666, or all access) even if the original files on the filesystem were with more restrictive permissions. This may result in files having more lax permissions than intended when such archive is extracted.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00023.html
- https://bugs.php.net/bug.php?id=79082
- https://lists.debian.org/debian-lts-announce/2020/03/msg00034.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-7063
- https://security.gentoo.org/glsa/202003-57
- https://usn.ubuntu.com/4330-1/
- https://www.debian.org/security/2020/dsa-4717
- https://www.debian.org/security/2020/dsa-4719
- https://www.tenable.com/security/tns-2021-14
