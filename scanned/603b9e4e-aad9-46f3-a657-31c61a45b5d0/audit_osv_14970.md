# [H] CVE-2019-12749

## Summary
Severity: High
Advisory: CVE-2019-12749
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-06-11
Source: https://osv.dev/vulnerability/CVE-2019-12749
Type: osv

## Details
dbus before 1.10.28, 1.12.x before 1.12.16, and 1.13.x before 1.13.12, as used in DBusServer in Canonical Upstart in Ubuntu 14.04 (and in some, less common, uses of dbus-daemon), allows cookie spoofing because of symlink mishandling in the reference implementation of DBUS_COOKIE_SHA1 in the libdbus library. (This only affects the DBUS_COOKIE_SHA1 authentication mechanism.) A malicious client with write access to its own home directory could manipulate a ~/.dbus-keyrings symlink to cause a DBusServer with a different uid to read and write in unintended locations. In the worst case, this could result in the DBusServer reusing a cookie that is known to the malicious client, and treating that cookie as evidence that a subsequent client connection came from an attacker-chosen uid, allowing authentication bypass.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00092.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00026.html
- http://www.securityfocus.com/bid/108751
- https://lists.debian.org/debian-lts-announce/2019/06/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V2CQF37O73VH2JDVX2ILX2KD2KLXLQOU/
- https://seclists.org/bugtraq/2019/Jun/16
- https://usn.ubuntu.com/4015-2/
- http://www.openwall.com/lists/oss-security/2019/06/11/2
- https://access.redhat.com/errata/RHSA-2019:1726
- https://access.redhat.com/errata/RHSA-2019:2868
- https://access.redhat.com/errata/RHSA-2019:2870
- https://access.redhat.com/errata/RHSA-2019:3707
- https://security.gentoo.org/glsa/201909-08
- https://security.netapp.com/advisory/ntap-20241206-0010/
- https://usn.ubuntu.com/4015-1/
- https://www.debian.org/security/2019/dsa-4462
- https://www.openwall.com/lists/oss-security/2019/06/11/2
