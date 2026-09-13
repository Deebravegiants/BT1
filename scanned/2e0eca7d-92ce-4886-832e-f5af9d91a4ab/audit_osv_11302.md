# [H] CVE-2017-7303

## Summary
Severity: High
Advisory: CVE-2017-7303
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-29
Source: https://osv.dev/vulnerability/CVE-2017-7303
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, is vulnerable to an invalid read (of size 4) because of missing a check (in the find_link function) for null headers before attempting to match them. This vulnerability causes Binutils utilities like strip to crash.

## References
- http://www.securityfocus.com/bid/97213
- https://sourceware.org/bugzilla/show_bug.cgi?id=20922
