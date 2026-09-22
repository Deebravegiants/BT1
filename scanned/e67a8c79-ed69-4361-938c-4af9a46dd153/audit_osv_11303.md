# [H] CVE-2017-7304

## Summary
Severity: High
Advisory: CVE-2017-7304
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-29
Source: https://osv.dev/vulnerability/CVE-2017-7304
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, is vulnerable to an invalid read (of size 8) because of missing a check (in the copy_special_section_fields function) for an invalid sh_link field before attempting to follow it. This vulnerability causes Binutils utilities like strip to crash.

## References
- http://www.securityfocus.com/bid/97215
- https://sourceware.org/bugzilla/show_bug.cgi?id=20931
