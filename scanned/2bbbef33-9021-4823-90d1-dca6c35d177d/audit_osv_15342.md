# [M] CVE-2019-1559

## Summary
Severity: Medium
Advisory: CVE-2019-1559
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-02-27
Source: https://osv.dev/vulnerability/CVE-2019-1559
Type: osv

## Details
If an application encounters a fatal protocol error and then calls SSL_shutdown() twice (once to send a close_notify, and once to receive one) then OpenSSL can respond differently to the calling application if a 0 byte record is received with invalid padding compared to if a 0 byte record is received with an invalid MAC. If the application then behaves differently based on that in a way that is detectable to the remote peer, then this amounts to a padding oracle that could be used to decrypt data. In order for this to be exploitable "non-stitched" ciphersuites must be in use. Stitched ciphersuites are optimised implementations of certain commonly used ciphersuites. Also the application must call SSL_shutdown() twice even if a protocol error has occurred (applications should not do this but some do anyway). Fixed in OpenSSL 1.0.2r (Affected 1.0.2-1.0.2q).

## References
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=e9bbefbf0f24c57645e7ad6a5a71ae649d18ac8e
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EWC42UXL5GHTU5G77VKBF6JYUUNGSHOM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y3IVFGSERAZLNJCK35TEM2R4726XIH3Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZBEV5QGDRFUZDMNECFXUSN5FMYOZDE4V/
- https://support.f5.com/csp/article/K18549143?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/4376-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00046.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00049.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00080.html
- http://www.securityfocus.com/bid/107174
- https://access.redhat.com/errata/RHSA-2019:2304
- https://access.redhat.com/errata/RHSA-2019:2437
- https://access.redhat.com/errata/RHSA-2019:2439
- https://access.redhat.com/errata/RHSA-2019:2471
- https://access.redhat.com/errata/RHSA-2019:3929
- https://access.redhat.com/errata/RHSA-2019:3931
- https://kc.mcafee.com/corporate/index?page=content&id=SB10282
