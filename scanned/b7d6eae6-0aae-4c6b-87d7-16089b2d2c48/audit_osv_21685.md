# [M] CVE-2021-45340

## Summary
Severity: Medium
Advisory: CVE-2021-45340
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-25
Source: https://osv.dev/vulnerability/CVE-2021-45340
Type: osv

## Details
In Libsixel prior to and including v1.10.3, a NULL pointer dereference in the stb_image.h component of libsixel allows attackers to cause a denial of service (DOS) via a crafted PICT file.

## References
- https://github.com/libsixel/libsixel/issues/51
