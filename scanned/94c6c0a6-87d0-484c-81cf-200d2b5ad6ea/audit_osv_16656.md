# [H] CVE-2019-8904

## Summary
Severity: High
Advisory: CVE-2019-8904
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-18
Source: https://osv.dev/vulnerability/CVE-2019-8904
Type: osv

## Details
do_bid_note in readelf.c in libmagic.a in file 5.35 has a stack-based buffer over-read, related to file_printf and file_vprintf.

## References
- http://www.securityfocus.com/bid/107130
- https://usn.ubuntu.com/3911-1/
- https://bugs.astron.com/view.php?id=62
