# [M] CVE-2017-12797

## Summary
Severity: Medium
Advisory: CVE-2017-12797
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-12797
Type: osv

## Details
Integer overflow in the INT123_parse_new_id3 function in the ID3 parser in mpg123 before 1.25.5 on 32-bit platforms allows remote attackers to cause a denial of service via a crafted file, which triggers a heap-based buffer overflow.

## References
- https://sourceforge.net/p/mpg123/bugs/254/
- https://sourceforge.net/p/mpg123/mailman/message/35987663/
