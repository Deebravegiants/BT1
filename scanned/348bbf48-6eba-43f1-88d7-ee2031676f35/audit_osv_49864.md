# [M] CVE-2019-20056

## Summary
Severity: Medium
Advisory: CVE-2019-20056
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-29
Source: https://osv.dev/vulnerability/CVE-2019-20056
Type: osv

## Details
stb_image.h (aka the stb image loader) 2.23, as used in libsixel and other products, has an assertion failure in stbi__shiftsigned.

## References
- https://github.com/saitoha/libsixel/issues/126
