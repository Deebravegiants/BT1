# [H] CVE-2016-5420

## Summary
Severity: High
Advisory: CVE-2016-5420
Aliases: CURL-CVE-2016-5420
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-08-10
Source: https://osv.dev/vulnerability/CVE-2016-5420
Type: osv

## Details
curl and libcurl before 7.50.1 do not check the client certificate when choosing the TLS connection to reuse, which might allow remote attackers to hijack the authentication of the connection by leveraging a previously created connection with a different client certificate.

## References
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00011.html
- http://www.securityfocus.com/bid/92309
- http://www.securitytracker.com/id/1036537
- http://www.securitytracker.com/id/1036739
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.563059
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GLPXQQKURBQFM4XM6645VRPTOE2AWG33/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K3GQH4V3XAQ5Z53AMQRDEC3C3UHTW7QR/
- https://source.android.com/security/bulletin/2016-12-01.html
- https://www.tenable.com/security/tns-2016-18
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00094.html
- http://rhn.redhat.com/errata/RHSA-2016-2575.html
- http://rhn.redhat.com/errata/RHSA-2016-2957.html
- http://www.debian.org/security/2016/dsa-3638
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.ubuntu.com/usn/USN-3048-1
- https://access.redhat.com/errata/RHSA-2018:3558
- https://security.gentoo.org/glsa/201701-47
- https://curl.haxx.se/docs/adv_20160803B.html
