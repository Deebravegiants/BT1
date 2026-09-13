# [H] CVE-2018-10841

## Summary
Severity: High
Advisory: CVE-2018-10841
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-20
Source: https://osv.dev/vulnerability/CVE-2018-10841
Type: osv

## Details
glusterfs is vulnerable to privilege escalation on gluster server nodes. An authenticated gluster client via TLS could use gluster cli with --remote-host command to add it self to trusted storage pool and perform privileged gluster operations like adding other machines to trusted storage pool, start, stop, and delete volumes.

## References
- https://access.redhat.com/errata/RHSA-2018:1954
- https://access.redhat.com/errata/RHSA-2018:1955
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10841
- https://review.gluster.org/#/c/20328/
