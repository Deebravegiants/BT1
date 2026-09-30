# [M] CVE-2018-7874

## Summary
Severity: Medium
Advisory: CVE-2018-7874
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-08
Source: https://osv.dev/vulnerability/CVE-2018-7874
Type: osv

## Details
An invalid memory address dereference was discovered in strlenext in util/decompile.c in libming 0.4.8. The vulnerability causes a segmentation fault and application crash, which leads to denial of service.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=892260
- https://github.com/libming/libming/issues/115
