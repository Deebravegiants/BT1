# [H] CVE-2016-1978

## Summary
Severity: High
Advisory: CVE-2016-1978
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2016-03-13
Source: https://osv.dev/vulnerability/CVE-2016-1978
Type: osv

## Details
Use-after-free vulnerability in the ssl3_HandleECDHServerKeyExchange function in Mozilla Network Security Services (NSS) before 3.21, as used in Mozilla Firefox before 44.0, allows remote attackers to cause a denial of service or possibly have unspecified other impact by making an SSL (1) DHE or (2) ECDHE handshake at a time of high memory consumption.

## References
- http://www.securitytracker.com/id/1035258
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00068.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00093.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securityfocus.com/bid/84275
- http://www.securityfocus.com/bid/91787
- https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS/NSS_3.21_release_notes
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00050.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.ubuntu.com/usn/USN-2973-1
- https://bto.bluecoat.com/security-advisory/sa124
- https://security.gentoo.org/glsa/201605-06
- http://www.mozilla.org/security/announce/2016/mfsa2016-15.html
- http://rhn.redhat.com/errata/RHSA-2016-0591.html
- http://rhn.redhat.com/errata/RHSA-2016-0685.html
- http://rhn.redhat.com/errata/RHSA-2016-0684.html
- http://www.debian.org/security/2016/dsa-3688
- https://bugzilla.mozilla.org/show_bug.cgi?id=1209546
