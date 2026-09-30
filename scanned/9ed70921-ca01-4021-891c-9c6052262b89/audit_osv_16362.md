# [M] CVE-2019-6129

## Summary
Severity: Medium
Advisory: CVE-2019-6129
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-11
Source: https://osv.dev/vulnerability/CVE-2019-6129
Type: osv

## Details
png_create_info_struct in png.c in libpng 1.6.36 has a memory leak, as demonstrated by pngcp. NOTE: a third party has stated "I don't think it is libpng's job to free this buffer.

## References
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://github.com/glennrp/libpng/issues/269
