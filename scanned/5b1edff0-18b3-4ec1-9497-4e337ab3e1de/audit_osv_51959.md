# [M] CVE-2021-46313

## Summary
Severity: Medium
Advisory: CVE-2021-46313
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2021-46313
Type: osv

## Details
The binary MP4Box in GPAC v1.0.1 was discovered to contain a segmentation fault via the function __memmove_avx_unaligned_erms (). This vulnerability can lead to a Denial of Service (DoS).

## References
- https://github.com/gpac/gpac/issues/2039
