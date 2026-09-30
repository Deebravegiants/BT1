# [M] CVE-2021-46239

## Summary
Severity: Medium
Advisory: CVE-2021-46239
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2021-46239
Type: osv

## Details
The binary MP4Box in GPAC v1.1.0 was discovered to contain an invalid free vulnerability via the function gf_free () at utils/alloc.c. This vulnerability can lead to a Denial of Service (DoS).

## References
- https://github.com/gpac/gpac/issues/2026
