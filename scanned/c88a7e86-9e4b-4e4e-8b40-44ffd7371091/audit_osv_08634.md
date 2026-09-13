# [C] CVE-2016-5008

## Summary
Severity: Critical
Advisory: CVE-2016-5008
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-13
Source: https://osv.dev/vulnerability/CVE-2016-5008
Type: osv

## Details
libvirt before 2.0.0 improperly disables password checking when the password on a VNC server is set to an empty string, which allows remote attackers to bypass authentication and establish a VNC session by connecting to the server.

## References
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00054.html
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00055.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00024.html
- http://www.securityfocus.com/bid/91562
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DZZMOMRXNPALA34XDF5NK363KDLAYSTL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QTQF6LXKEEMJG4VOOCIAPJAD6ACBYP4W/
- https://usn.ubuntu.com/3576-1/
- http://rhn.redhat.com/errata/RHSA-2016-2577.html
- http://security.libvirt.org/2016/0001.html
- http://www.debian.org/security/2016/dsa-3613
- https://bugzilla.redhat.com/show_bug.cgi?id=1180092
