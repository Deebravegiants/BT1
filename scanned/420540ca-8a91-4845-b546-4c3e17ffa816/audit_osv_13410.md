# [H] CVE-2018-19762

## Summary
Severity: High
Advisory: CVE-2018-19762
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-30
Source: https://osv.dev/vulnerability/CVE-2018-19762
Type: osv

## Details
There is a heap-based buffer overflow at fromsixel.c (function: image_buffer_resize) in libsixel 1.8.2 that will cause a denial of service or possibly unspecified other impact.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1649199
