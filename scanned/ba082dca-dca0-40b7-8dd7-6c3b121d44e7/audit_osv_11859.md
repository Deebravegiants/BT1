# [M] CVE-2018-0734

## Summary
Severity: Medium
Advisory: CVE-2018-0734
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-30
Source: https://osv.dev/vulnerability/CVE-2018-0734
Type: osv

## Details
The OpenSSL DSA signature algorithm has been shown to be vulnerable to a timing side channel attack. An attacker could use variations in the signing algorithm to recover the private key. Fixed in OpenSSL 1.1.1a (Affected 1.1.1). Fixed in OpenSSL 1.1.0j (Affected 1.1.0-1.1.0i). Fixed in OpenSSL 1.0.2q (Affected 1.0.2-1.0.2p).

## References
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=43e6a58d4991a451daf4891ff05a48735df871ac
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=8abfe72e8c1de1b95f50aa0d9134803b4d00070f
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=ef11e19d1365eea2b1851e6f540a0bf365d303e7
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EWC42UXL5GHTU5G77VKBF6JYUUNGSHOM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y3IVFGSERAZLNJCK35TEM2R4726XIH3Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZBEV5QGDRFUZDMNECFXUSN5FMYOZDE4V/
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00056.html
- http://www.securityfocus.com/bid/105758
- https://access.redhat.com/errata/RHSA-2019:2304
- https://access.redhat.com/errata/RHSA-2019:3700
- https://access.redhat.com/errata/RHSA-2019:3932
- https://access.redhat.com/errata/RHSA-2019:3933
- https://access.redhat.com/errata/RHSA-2019:3935
- https://nodejs.org/en/blog/vulnerability/november-2018-security-releases/
- https://security.netapp.com/advisory/ntap-20181105-0002/
- https://security.netapp.com/advisory/ntap-20190118-0002/
- https://security.netapp.com/advisory/ntap-20190423-0002/
- https://usn.ubuntu.com/3840-1/
- https://www.debian.org/security/2018/dsa-4348
