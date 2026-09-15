# [H] CVE-2017-11143

## Summary
Severity: High
Advisory: CVE-2017-11143
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2017-11143
Type: osv

## Details
In PHP before 5.6.31, an invalid free in the WDDX deserialization of boolean parameters could be used by attackers able to inject XML for deserialization to crash the PHP interpreter, related to an invalid free for an empty boolean element in ext/wddx/wddx.c.

## References
- http://www.securityfocus.com/bid/99553
- https://git.php.net/?p=php-src.git%3Ba=commit%3Bh=2aae60461c2ff7b7fbcdd194c789ac841d0747d7
- https://www.tenable.com/security/tns-2017-12
- http://php.net/ChangeLog-5.php
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://www.debian.org/security/2018/dsa-4081
- http://openwall.com/lists/oss-security/2017/07/10/6
- https://bugs.php.net/bug.php?id=74145
