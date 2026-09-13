# [H] CVE-2018-1000156

## Summary
Severity: High
Advisory: CVE-2018-1000156
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-06
Source: https://osv.dev/vulnerability/CVE-2018-1000156
Type: osv

## Details
GNU Patch version 2.7.6 contains an input validation vulnerability when processing patch files, specifically the EDITOR_PROGRAM invocation (using ed) can result in code execution. This attack appear to be exploitable via a patch file processed via the patch utility. This is similar to FreeBSD's CVE-2015-1418 however although they share a common ancestry the code bases have diverged over time.

## References
- https://seclists.org/bugtraq/2019/Aug/29
- http://packetstormsecurity.com/files/154124/GNU-patch-Command-Injection-Directory-Traversal.html
- https://seclists.org/bugtraq/2019/Jul/54
- https://web.archive.org/web/20180405231329/https://twitter.com/kurtseifried/status/982028968877436928
- https://access.redhat.com/errata/RHSA-2018:2091
- https://access.redhat.com/errata/RHSA-2018:2093
- https://access.redhat.com/errata/RHSA-2018:2097
- https://lists.debian.org/debian-lts-announce/2018/04/msg00013.html
- https://security.gentoo.org/glsa/201904-17
- https://twitter.com/kurtseifried/status/982028968877436928
- http://rachelbythebay.com/w/2018/04/05/bangpatch/
- https://access.redhat.com/errata/RHSA-2018:1199
- https://access.redhat.com/errata/RHSA-2018:2095
- https://usn.ubuntu.com/3624-2/
- https://access.redhat.com/errata/RHSA-2018:2092
- https://access.redhat.com/errata/RHSA-2018:2094
- https://savannah.gnu.org/bugs/index.php?53566
- https://usn.ubuntu.com/3624-1/
- https://access.redhat.com/errata/RHSA-2018:1200
- https://access.redhat.com/errata/RHSA-2018:2096
