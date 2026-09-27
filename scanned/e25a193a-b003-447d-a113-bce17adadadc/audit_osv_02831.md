# [M] ALPINE-CVE-2023-3316

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-3316
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-3316
Type: osv

## Affected
- Alpine:v3.15: `tiff` — affected >=0 <4.4.0-r4
- Alpine:v3.16: `tiff` — affected >=0 <4.4.0-r4
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r4

## Details
A NULL pointer dereference in TIFFClose() is caused by a failure to open an output file (non-existent path or a path that requires permissions like /dev/null) while specifying zones.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-3316
