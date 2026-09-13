# [C] CVE-2017-16931

## Summary
Severity: Critical
Advisory: CVE-2017-16931
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-23
Source: https://osv.dev/vulnerability/CVE-2017-16931
Type: osv

## Details
parser.c in libxml2 before 2.9.5 mishandles parameter-entity references because the NEXTL macro calls the xmlParserHandlePEReference function in the case of a '%' character in a DTD name.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00041.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- http://xmlsoft.org/news.html
- https://bugzilla.gnome.org/show_bug.cgi?id=766956
- https://github.com/GNOME/libxml2/commit/e26630548e7d138d2c560844c43820b6767251e3
