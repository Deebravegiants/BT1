# [M] CVE-2018-18384

## Summary
Severity: Medium
Advisory: CVE-2018-18384
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-16
Source: https://osv.dev/vulnerability/CVE-2018-18384
Type: osv

## Details
Info-ZIP UnZip 6.0 has a buffer overflow in list.c, when a ZIP archive has a crafted relationship between the compressed-size value and the uncompressed-size value, because a buffer size is 10 and is supposed to be 12.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00009.html
- https://access.redhat.com/errata/RHSA-2019:2159
- https://bugzilla.suse.com/show_bug.cgi?id=1110194
- https://sourceforge.net/p/infozip/bugs/53/
