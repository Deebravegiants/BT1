# [M] CVE-2020-11721

## Summary
Severity: Medium
Advisory: CVE-2020-11721
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-04-12
Source: https://osv.dev/vulnerability/CVE-2020-11721
Type: osv

## Details
load_png in loader.c in libsixel.a in libsixel 1.8.6 has an uninitialized pointer leading to an invalid call to free, which can cause a denial of service.

## References
- https://github.com/saitoha/libsixel/issues/134
