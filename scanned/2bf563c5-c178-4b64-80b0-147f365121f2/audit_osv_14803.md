# [C] CVE-2019-11500

## Summary
Severity: Critical
Advisory: CVE-2019-11500
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/CVE-2019-11500
Type: osv

## Details
In Dovecot before 2.2.36.4 and 2.3.x before 2.3.7.2 (and Pigeonhole before 0.5.7.2), protocol processing can fail for quoted strings. This occurs because '\0' characters are mishandled, and can lead to out-of-bounds writes and remote code execution.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3GYTZLLDNIFWT7D7JSB25ERJNMOR4CQ3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KVHY3MU2OK2EWZJFGNDSAOMD42L7DFPX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YSJVVVRAE3SITC2ZLGCPMFDN3WVYZBWF/
- https://access.redhat.com/errata/RHSA-2019:2822
- https://access.redhat.com/errata/RHSA-2019:2836
- https://access.redhat.com/errata/RHSA-2019:2885
- https://lists.debian.org/debian-lts-announce/2019/08/msg00035.html
- https://security.gentoo.org/glsa/201908-29
- https://www.dovecot.org/security.html
- https://dovecot.org/pipermail/dovecot-news/2019-August/000417.html
- http://www.openwall.com/lists/oss-security/2019/08/28/3
