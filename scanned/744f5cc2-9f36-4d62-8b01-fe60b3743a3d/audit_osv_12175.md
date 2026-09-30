# [M] CVE-2018-10768

## Summary
Severity: Medium
Advisory: CVE-2018-10768
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-06
Source: https://osv.dev/vulnerability/CVE-2018-10768
Type: osv

## Details
There is a NULL pointer dereference in the AnnotPath::getCoordsLength function in Annot.h in an Ubuntu package for Poppler 0.24.5. A crafted input will lead to a remote denial of service attack. Later Ubuntu packages such as for Poppler 0.41.0 are not affected.

## References
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3140
- https://access.redhat.com/errata/RHSA-2018:3505
- https://lists.debian.org/debian-lts-announce/2018/10/msg00024.html
- https://usn.ubuntu.com/3647-1/
- https://bugs.freedesktop.org/show_bug.cgi?id=106408
