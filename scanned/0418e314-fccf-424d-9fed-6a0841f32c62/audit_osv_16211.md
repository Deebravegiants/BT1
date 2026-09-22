# [M] CVE-2019-3572

## Summary
Severity: Medium
Advisory: CVE-2019-3572
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-02
Source: https://osv.dev/vulnerability/CVE-2019-3572
Type: osv

## Details
An issue was discovered in libming 0.4.8. There is a heap-based buffer over-read in the function writePNG in the file util/dbl2png.c of the dbl2png command-line program. Because this is associated with an erroneous call to png_write_row in libpng, an out-of-bounds write might occur for some memory layouts.

## References
- https://github.com/libming/libming/issues/169
