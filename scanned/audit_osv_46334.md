# [H] CVE-2000-1254

## Summary
Severity: High
Advisory: CVE-2000-1254
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-05-05
Source: https://osv.dev/vulnerability/CVE-2000-1254
Type: osv

## Details
crypto/rsa/rsa_gen.c in OpenSSL before 0.9.6 mishandles C bitwise-shift operations that exceed the size of an expression, which makes it easier for remote attackers to defeat cryptographic protection mechanisms by leveraging improper RSA key generation on 64-bit HP-UX platforms.

## References
- http://marc.info/?l=openssl-users&m=95961024500509
- http://www-01.ibm.com/support/docview.wss?uid=swg21995039
- http://www.openwall.com/lists/oss-security/2016/05/04/17
- http://www.securityfocus.com/bid/90109
- http://www.securitytracker.com/id/1035750
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=db82b8f9bd432a59aea8e1014694e15fc457c2bb
