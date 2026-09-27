# [H] ALPINE-CVE-2024-6239

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-6239
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-6239
Type: osv

## Affected
- Alpine:v3.21: `poppler` — affected >=0 <24.02.0-r2
- Alpine:v3.22: `poppler` — affected >=0 <24.02.0-r2
- Alpine:v3.23: `poppler` — affected >=0 <24.02.0-r2
- Alpine:v3.24: `poppler` — affected >=0 <24.02.0-r2

## Details
A flaw was found in the Poppler's Pdfinfo utility. This issue occurs when using -dests parameter with pdfinfo utility. By using certain malformed input files, an attacker could cause the utility to crash, leading to a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-6239
