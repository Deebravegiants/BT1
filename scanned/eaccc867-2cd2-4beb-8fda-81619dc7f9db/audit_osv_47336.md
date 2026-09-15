# [M] CVE-2016-2830

## Summary
Severity: Medium
Advisory: CVE-2016-2830
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2016-08-05
Source: https://osv.dev/vulnerability/CVE-2016-2830
Type: osv

## Details
Mozilla Firefox before 48.0 and Firefox ESR 45.x before 45.3 preserve the network connection used for favicon resource retrieval after the associated browser window is closed, which makes it easier for remote web servers to track users by observing network traffic from multiple IP addresses.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00029.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/92261
- http://www.securitytracker.com/id/1036508
- http://www.ubuntu.com/usn/USN-3044-1
- http://rhn.redhat.com/errata/RHSA-2016-1551.html
- http://www.debian.org/security/2016/dsa-3640
- http://www.mozilla.org/security/announce/2016/mfsa2016-63.html
- https://security.gentoo.org/glsa/201701-15
- https://bugzilla.mozilla.org/show_bug.cgi?id=1255270
