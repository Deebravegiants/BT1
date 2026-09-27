# [M] CVE-2017-7209

## Summary
Severity: Medium
Advisory: CVE-2017-7209
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-21
Source: https://osv.dev/vulnerability/CVE-2017-7209
Type: osv

## Details
The dump_section_as_bytes function in readelf in GNU Binutils 2.28 accesses a NULL pointer while reading section contents in a corrupt binary, leading to a program crash.

## References
- http://www.securityfocus.com/bid/96994
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=21135
