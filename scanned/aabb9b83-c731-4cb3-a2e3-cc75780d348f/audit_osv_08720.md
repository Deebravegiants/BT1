# [M] CVE-2016-5404

## Summary
Severity: Medium
Advisory: CVE-2016-5404
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-07
Source: https://osv.dev/vulnerability/CVE-2016-5404
Type: osv

## Details
The cert_revoke command in FreeIPA does not check for the "revoke certificate" permission, which allows remote authenticated users to revoke arbitrary certificates by leveraging the "retrieve certificate" permission.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3PZ2ZQTMGC2UBRNHXVVOY3PJDOBP4CP4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S5OROLKFSY5QRQS7NGBNDP5QMOBV3XMZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VQDYWANTMDFZP3HTGSEOA2IONVUITYX5/
- http://rhn.redhat.com/errata/RHSA-2016-1797.html
- http://www.openwall.com/lists/oss-security/2016/08/17/9
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/92525
- https://fedorahosted.org/freeipa/ticket/6232
- https://git.fedorahosted.org/cgit/freeipa.git/commit/?id=cf74584d0f772f3f5eccc1d30c001e4212a104fd
