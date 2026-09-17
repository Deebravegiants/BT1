# [M] CVE-2018-10733

## Summary
Severity: Medium
Advisory: CVE-2018-10733
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-04
Source: https://osv.dev/vulnerability/CVE-2018-10733
Type: osv

## Details
There is a heap-based buffer over-read in the function ft_font_face_hash of gxps-fonts.c in libgxps through 0.3.0. A crafted input will lead to a remote denial of service attack.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00005.html
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3140
- https://access.redhat.com/errata/RHSA-2018:3505
- https://bugzilla.redhat.com/show_bug.cgi?id=1574844
