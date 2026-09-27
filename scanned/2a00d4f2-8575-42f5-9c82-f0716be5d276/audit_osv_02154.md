# [H] ALPINE-CVE-2021-28676

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28676
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28676
Type: osv

## Affected
- Alpine:v3.14: `py3-pillow` — affected >=0 <8.2.0-r0
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.2.0-r0

## Details
An issue was discovered in Pillow before 8.2.0. For FLI data, FliDecode did not properly check that the block advance was non-zero, potentially leading to an infinite loop on load.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28676
