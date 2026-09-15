# [H] CVE-2017-14412

## Summary
Severity: High
Advisory: CVE-2017-14412
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-13
Source: https://osv.dev/vulnerability/CVE-2017-14412
Type: osv

## Details
An invalid memory write was discovered in copy_mp in interface.c in mpglibDBL, as used in MP3Gain version 1.5.2. The vulnerability causes a denial of service (segmentation fault and application crash) or possibly unspecified other impact.

## References
- https://blogs.gentoo.org/ago/2017/09/08/mp3gain-invalid-memory-write-in-copy_mp-mpglibdblinterface-c/
