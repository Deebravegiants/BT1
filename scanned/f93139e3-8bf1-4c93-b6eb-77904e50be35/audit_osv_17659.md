# [M] CVE-2020-18768

## Summary
Severity: Medium
Advisory: CVE-2020-18768
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-18768
Type: osv

## Details
There exists one heap buffer overflow in _TIFFmemcpy in tif_unix.c in libtiff 4.0.10, which allows an attacker to cause a denial-of-service through a crafted tiff file.

## References
- http://bugzilla.maptools.org/show_bug.cgi?id=2848
