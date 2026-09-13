# [M] CVE-2019-11459

## Summary
Severity: Medium
Advisory: CVE-2019-11459
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/CVE-2019-11459
Type: osv

## Details
The tiff_document_render() and tiff_document_get_thumbnail() functions in the TIFF document backend in GNOME Evince through 3.32.0 did not handle errors from TIFFReadRGBAImageOriented(), leading to uninitialized memory use when processing certain TIFF image files.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7LU4YZK5S46TZAH4J3NYYUYFMOC47LJG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YJ6R7NMY44IHIQIY24CV3WV2GLGJPQPZ/
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00089.html
- https://access.redhat.com/errata/RHSA-2019:3553
- https://lists.debian.org/debian-lts-announce/2019/08/msg00013.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00014.html
- https://seclists.org/bugtraq/2020/Feb/18
- https://usn.ubuntu.com/3959-1/
- https://www.debian.org/security/2020/dsa-4624
- https://gitlab.gnome.org/GNOME/evince/issues/1129
