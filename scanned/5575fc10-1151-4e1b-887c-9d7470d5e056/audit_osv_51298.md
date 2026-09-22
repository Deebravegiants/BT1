# [H] CVE-2021-27799

## Summary
Severity: High
Advisory: CVE-2021-27799
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2021-27799
Type: osv

## Details
ean_leading_zeroes in backend/upcean.c in Zint Barcode Generator 2.9.1 has a stack-based buffer overflow that is reachable from the C API through an application that includes the Zint Barcode Generator library code.

## References
- http://zint.org.uk/Manual.aspx?type=p&page=3
- http://zint.org.uk/Manual.aspx?type=p&page=4
- http://zint.org.uk/Manual.aspx?type=p&page=5
- https://sourceforge.net/p/zint/code/ci/7f8c8114f31c09a986597e0ba63a49f96150368a/
- https://sourceforge.net/p/zint/tickets/218/
