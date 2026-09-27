# [M] CVE-2018-13988

## Summary
Severity: Medium
Advisory: CVE-2018-13988
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-25
Source: https://osv.dev/vulnerability/CVE-2018-13988
Type: osv

## Details
Poppler through 0.62 contains an out of bounds read vulnerability due to an incorrect memory access that is not mapped in its memory space, as demonstrated by pdfunite. This can result in memory corruption and denial of service. This may be exploitable when a victim opens a specially crafted PDF file.

## References
- http://packetstormsecurity.com/files/148661/PDFunite-0.62.0-Buffer-Overflow.html
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3140
- https://access.redhat.com/errata/RHSA-2018:3505
- https://lists.debian.org/debian-lts-announce/2018/10/msg00024.html
- https://usn.ubuntu.com/3757-1/
- https://bugzilla.novell.com/show_bug.cgi?id=CVE-2018-13988
- https://bugzilla.redhat.com/show_bug.cgi?id=1602838
- https://cgit.freedesktop.org/poppler/poppler/commit/?id=004e3c10df0abda214f0c293f9e269fdd979c5ee
