# [H] CVE-2021-36530

## Summary
Severity: High
Advisory: CVE-2021-36530
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/CVE-2021-36530
Type: osv

## Details
ngiflib 0.4 has a heap overflow in GetByteStr() at ngiflib.c:108 in NGIFLIB_NO_FILE mode, GetByteStr() copy memory buffer without checking the boundary.

## References
- https://github.com/miniupnp/ngiflib/issues/19
