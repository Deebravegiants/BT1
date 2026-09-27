# [M] CVE-2018-14661

## Summary
Severity: Medium
Advisory: CVE-2018-14661
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/CVE-2018-14661
Type: osv

## Details
It was found that usage of snprintf function in feature/locks translator of glusterfs server 3.8.4, as shipped with Red Hat Gluster Storage, was vulnerable to a format string attack. A remote, authenticated attacker could use this flaw to cause remote denial of service.

## References
- https://access.redhat.com/errata/RHSA-2018:3431
- https://access.redhat.com/errata/RHSA-2018:3432
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2018/11/msg00003.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14661
