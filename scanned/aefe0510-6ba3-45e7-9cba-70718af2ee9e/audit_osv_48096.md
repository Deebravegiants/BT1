# [H] CVE-2017-18189

## Summary
Severity: High
Advisory: CVE-2017-18189
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-15
Source: https://osv.dev/vulnerability/CVE-2017-18189
Type: osv

## Details
In the startread function in xa.c in Sound eXchange (SoX) through 14.4.2, a corrupt header specifying zero channels triggers an infinite loop with a resultant NULL pointer dereference, which may allow a remote attacker to cause a denial-of-service.

## References
- https://public-inbox.org/sox-devel/20171109114554.16297-1-mans%40mansr.com/raw
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/62RARFRXGKPNNFFNVDV7DHJSOKAIZ3CX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EUKFZQSZG2ABMTAMOGBMY7MJNSGEIYTL/
- https://access.redhat.com/errata/RHSA-2019:2283
- https://lists.debian.org/debian-lts-announce/2019/02/msg00042.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=881121
