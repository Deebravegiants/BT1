# [H] CVE-2017-17973

## Summary
Severity: High
Advisory: CVE-2017-17973
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-29
Source: https://osv.dev/vulnerability/CVE-2017-17973
Type: osv

## Details
In LibTIFF 4.0.8, there is a heap-based use-after-free in the t2p_writeproc function in tiff2pdf.c. NOTE: there is a third-party report of inability to reproduce this issue

## References
- http://www.securityfocus.com/bid/102331
- http://bugzilla.maptools.org/show_bug.cgi?id=2769
- https://bugzilla.novell.com/show_bug.cgi?id=1074318
- https://bugzilla.redhat.com/show_bug.cgi?id=1530912
