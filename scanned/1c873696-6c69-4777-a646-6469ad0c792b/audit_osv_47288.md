# [M] CVE-2016-2217

## Summary
Severity: Medium
Advisory: CVE-2016-2217
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-01-30
Source: https://osv.dev/vulnerability/CVE-2016-2217
Type: osv

## Details
The OpenSSL address implementation in Socat 1.7.3.0 and 2.0.0-b8 does not use a prime number for the DH, which makes it easier for remote attackers to obtain the shared secret.

## References
- https://security.gentoo.org/glsa/201612-23
- http://www.openwall.com/lists/oss-security/2016/02/04/1
- http://www.dest-unreach.org/socat/contrib/socat-secadv7.html
- http://www.openwall.com/lists/oss-security/2016/02/01/4
