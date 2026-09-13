# [M] CVE-2017-6965

## Summary
Severity: Medium
Advisory: CVE-2017-6965
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-17
Source: https://osv.dev/vulnerability/CVE-2017-6965
Type: osv

## Details
readelf in GNU Binutils 2.28 writes to illegal addresses while processing corrupt input files containing symbol-difference relocations, leading to a heap-based buffer overflow.

## References
- https://security.gentoo.org/glsa/201709-02
- https://sourceware.org/bugzilla/show_bug.cgi?id=21137
