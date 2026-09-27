# [M] CVE-2017-3737

## Summary
Severity: Medium
Advisory: CVE-2017-3737
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-07
Source: https://osv.dev/vulnerability/CVE-2017-3737
Type: osv

## Details
OpenSSL 1.0.2 (starting from version 1.0.2b) introduced an "error state" mechanism. The intent was that if a fatal error occurred during a handshake then OpenSSL would move into the error state and would immediately fail if you attempted to continue the handshake. This works as designed for the explicit handshake functions (SSL_do_handshake(), SSL_accept() and SSL_connect()), however due to a bug it does not work correctly if SSL_read() or SSL_write() is called directly. In that scenario, if the handshake fails then a fatal error will be returned in the initial function call. If SSL_read()/SSL_write() is subsequently called by the application for the same SSL object then it will succeed and the data is passed without being decrypted/encrypted directly from the SSL/TLS record layer. In order to exploit this issue an application bug would have to be present that resulted in a call to SSL_read()/SSL_write() being issued after having already received a fatal error. OpenSSL version 1.0.2b-1.0.2m are affected. Fixed in OpenSSL 1.0.2n. OpenSSL 1.1.0 is not affected.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-179516.pdf
- https://www.tenable.com/security/tns-2017-16
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.securityfocus.com/bid/102103
- http://www.securitytracker.com/id/1039978
- https://access.redhat.com/errata/RHSA-2018:0998
- https://access.redhat.com/errata/RHSA-2018:2185
- https://access.redhat.com/errata/RHSA-2018:2186
- https://access.redhat.com/errata/RHSA-2018:2187
- https://security.FreeBSD.org/advisories/FreeBSD-SA-17:12.openssl.asc
- https://security.gentoo.org/glsa/201712-03
- https://security.netapp.com/advisory/ntap-20171208-0001/
- https://security.netapp.com/advisory/ntap-20180117-0002/
- https://security.netapp.com/advisory/ntap-20180419-0002/
- https://www.debian.org/security/2017/dsa-4065
- https://www.digitalmunition.me/2017/12/cve-2017-3737-openssl-security-bypass-vulnerability/
- https://www.openssl.org/news/secadv/20171207.txt
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
