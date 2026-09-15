# [H] CVE-2018-10907

## Summary
Severity: High
Advisory: CVE-2018-10907
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-10907
Type: osv

## Details
It was found that glusterfs server is vulnerable to multiple stack based buffer overflows due to functions in server-rpc-fopc.c allocating fixed size buffers using 'alloca(3)'. An authenticated attacker could exploit this by mounting a gluster volume and sending a string longer that the fixed buffer size to cause crash or potential code execution.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00035.html
- https://access.redhat.com/errata/RHSA-2018:2607
- https://access.redhat.com/errata/RHSA-2018:2608
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2018/09/msg00021.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10907
- https://review.gluster.org/#/c/glusterfs/+/21070/
