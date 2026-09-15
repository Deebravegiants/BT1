# [H] ALPINE-CVE-2022-42330

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-42330
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42330
Type: osv

## Affected
- Alpine:v3.18: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.19: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.20: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.21: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.22: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.23: `xen` — affected >=0 <4.17.0-r2
- Alpine:v3.24: `xen` — affected >=0 <4.17.0-r2

## Details
Guests can cause Xenstore crash via soft reset When a guest issues a "Soft Reset" (e.g. for performing a kexec) the libxl based Xen toolstack will normally perform a XS_RELEASE Xenstore operation. Due to a bug in xenstored this can result in a crash of xenstored. Any other use of XS_RELEASE will have the same impact.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42330
