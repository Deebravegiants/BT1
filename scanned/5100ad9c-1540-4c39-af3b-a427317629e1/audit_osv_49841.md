# [M] CVE-2019-19746

## Summary
Severity: Medium
Advisory: CVE-2019-19746
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-12
Source: https://osv.dev/vulnerability/CVE-2019-19746
Type: osv

## Details
make_arrow in arrow.c in Xfig fig2dev 3.2.7b allows a segmentation fault and out-of-bounds write because of an integer overflow via a large arrow type.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7XOY5NXUZ6JRBBPYA3CXWGRGQTSDVVG2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ILJM2G6NM5MMBKTT5CH23TAI6DJGNW36/
- https://sourceforge.net/p/mcj/tickets/57/
