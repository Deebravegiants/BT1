# [H] CVE-2019-3574

## Summary
Severity: High
Advisory: CVE-2019-3574
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-01-02
Source: https://osv.dev/vulnerability/CVE-2019-3574
Type: osv

## Details
In libsixel v1.8.2, there is a heap-based buffer over-read in the function load_jpeg() in the file loader.c, as demonstrated by img2sixel.

## References
- https://github.com/TeamSeri0us/pocs/tree/master/libsixel
- https://github.com/saitoha/libsixel/issues/83
