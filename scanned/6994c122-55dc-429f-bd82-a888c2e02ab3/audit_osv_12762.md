# [H] CVE-2018-14651

## Summary
Severity: High
Advisory: CVE-2018-14651
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/CVE-2018-14651
Type: osv

## Details
It was found that the fix for CVE-2018-10927, CVE-2018-10928, CVE-2018-10929, CVE-2018-10930, and CVE-2018-10926 was incomplete. A remote, authenticated attacker could use one of these flaws to execute arbitrary code, create arbitrary files, or cause denial of service on glusterfs server nodes via symlinks to relative paths.

## References
- https://access.redhat.com/errata/RHSA-2018:3431
- https://access.redhat.com/errata/RHSA-2018:3432
- https://lists.debian.org/debian-lts-announce/2018/11/msg00003.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14651
