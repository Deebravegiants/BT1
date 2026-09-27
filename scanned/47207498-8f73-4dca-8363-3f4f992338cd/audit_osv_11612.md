# [C] CVE-2017-9051

## Summary
Severity: Critical
Advisory: CVE-2017-9051
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9051
Type: osv

## Details
libav before 12.1 is vulnerable to an invalid read of size 1 due to NULL pointer dereferencing in the nsv_read_chunk function in libavformat/nsvdec.c.

## References
- http://www.securityfocus.com/bid/98548
- https://bugzilla.libav.org/show_bug.cgi?id=1039
- https://github.com/libav/libav/commit/fe6eea99efac66839052af547426518efd970b24
