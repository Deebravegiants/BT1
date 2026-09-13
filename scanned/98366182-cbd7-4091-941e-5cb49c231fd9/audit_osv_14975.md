# [H] CVE-2019-12779

## Summary
Severity: High
Advisory: CVE-2019-12779
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2019-06-07
Source: https://osv.dev/vulnerability/CVE-2019-12779
Type: osv

## Details
libqb before 1.0.5 allows local users to overwrite arbitrary files via a symlink attack, because it uses predictable filenames (under /dev/shm and /tmp) without O_EXCL.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00031.html
- http://www.securityfocus.com/bid/108691
- https://access.redhat.com/errata/RHSA-2019:3610
- https://github.com/ClusterLabs/libqb/releases/tag/v1.0.4
- https://github.com/ClusterLabs/libqb/releases/tag/v1.0.5
- https://security.gentoo.org/glsa/202107-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1695948
- https://github.com/ClusterLabs/libqb/issues/338
