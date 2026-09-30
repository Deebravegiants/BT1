# [M] get_headers() silently truncates after a null byte

## Summary
Severity: Medium
Advisory: BIT-libphp-2020-7066
Aliases: BIT-php-2020-7066, BIT-php-min-2020-7066, CVE-2020-7066
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2020-7066
Type: osv

## Affected
- Bitnami: `libphp` — affected >=7.4.0 <7.4.4

## Details
In PHP versions 7.2.x below 7.2.29, 7.3.x below 7.3.16 and 7.4.x below 7.4.4, while using get_headers() with user-supplied URL, if the URL contains zero (\0) character, the URL will be silently truncated at it. This may cause some software to make incorrect assumptions about the target of the get_headers() and possibly send some information to a wrong server.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00025.html
- https://bugs.php.net/bug.php?id=79329
- https://lists.debian.org/debian-lts-announce/2020/04/msg00021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-7066
- https://security.netapp.com/advisory/ntap-20200403-0001/
- https://usn.ubuntu.com/4330-2/
- https://www.debian.org/security/2020/dsa-4717
- https://www.debian.org/security/2020/dsa-4719
- https://www.tenable.com/security/tns-2021-14
