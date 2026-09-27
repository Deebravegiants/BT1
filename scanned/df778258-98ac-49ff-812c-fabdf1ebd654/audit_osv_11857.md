# [H] CVE-2018-0732

## Summary
Severity: High
Advisory: CVE-2018-0732
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-0732
Type: osv

## Details
During key agreement in a TLS handshake using a DH(E) based ciphersuite a malicious server can send a very large prime value to the client. This will cause the client to spend an unreasonably long period of time generating a key for this prime resulting in a hang until the client has finished. This could be exploited in a Denial Of Service attack. Fixed in OpenSSL 1.1.0i-dev (Affected 1.1.0-1.1.0h). Fixed in OpenSSL 1.0.2p-dev (Affected 1.0.2-1.0.2o).

## References
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=3984ef0b72831da8b3ece4745cac4f8575b19098
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=ea7abeeabf92b7aca160bdd0208636d4da69f4f4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EWC42UXL5GHTU5G77VKBF6JYUUNGSHOM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y3IVFGSERAZLNJCK35TEM2R4726XIH3Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZBEV5QGDRFUZDMNECFXUSN5FMYOZDE4V/
- http://www.securityfocus.com/bid/104442
- http://www.securitytracker.com/id/1041090
- https://access.redhat.com/errata/RHSA-2018:2552
- https://access.redhat.com/errata/RHSA-2018:2553
- https://access.redhat.com/errata/RHSA-2018:3221
- https://access.redhat.com/errata/RHSA-2018:3505
- https://access.redhat.com/errata/RHSA-2019:1296
- https://access.redhat.com/errata/RHSA-2019:1297
- https://access.redhat.com/errata/RHSA-2019:1543
- https://cert-portal.siemens.com/productcert/pdf/ssa-419820.pdf
- https://lists.debian.org/debian-lts-announce/2018/07/msg00043.html
- https://nodejs.org/en/blog/vulnerability/august-2018-security-releases/
- https://security.gentoo.org/glsa/201811-03
- https://security.netapp.com/advisory/ntap-20181105-0001/
- https://security.netapp.com/advisory/ntap-20190118-0002/
