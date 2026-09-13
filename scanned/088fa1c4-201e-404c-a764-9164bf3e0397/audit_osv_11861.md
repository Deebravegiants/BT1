# [M] CVE-2018-0737

## Summary
Severity: Medium
Advisory: CVE-2018-0737
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-04-16
Source: https://osv.dev/vulnerability/CVE-2018-0737
Type: osv

## Details
The OpenSSL RSA Key generation algorithm has been shown to be vulnerable to a cache timing side channel attack. An attacker with sufficient access to mount cache timing attacks during the RSA key generation process could recover the private key. Fixed in OpenSSL 1.1.0i-dev (Affected 1.1.0-1.1.0h). Fixed in OpenSSL 1.0.2p-dev (Affected 1.0.2b-1.0.2o).

## References
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=349a41da1ad88ad87825414752a8ff5fdd6a6c3f
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=6939eab03a6e23d2bd2c3f5e34fe1d48e542e787
- https://lists.debian.org/debian-lts-announce/2018/07/msg00043.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EWC42UXL5GHTU5G77VKBF6JYUUNGSHOM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y3IVFGSERAZLNJCK35TEM2R4726XIH3Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZBEV5QGDRFUZDMNECFXUSN5FMYOZDE4V/
- https://usn.ubuntu.com/3692-1/
- https://usn.ubuntu.com/3692-2/
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.tenable.com/security/tns-2018-12
- https://www.tenable.com/security/tns-2018-13
- https://www.tenable.com/security/tns-2018-14
- https://www.tenable.com/security/tns-2018-17
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.securityfocus.com/bid/103766
- http://www.securitytracker.com/id/1040685
- https://access.redhat.com/errata/RHSA-2018:3221
- https://access.redhat.com/errata/RHSA-2018:3505
- https://access.redhat.com/errata/RHSA-2019:3932
