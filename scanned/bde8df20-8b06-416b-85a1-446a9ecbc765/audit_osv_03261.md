# [M] ALPINE-CVE-2025-3198

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-3198
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-3198
Type: osv

## Affected
- Alpine:v3.21: `binutils` — affected >=0 <2.43.1-r3
- Alpine:v3.22: `binutils` — affected >=0 <2.44-r2
- Alpine:v3.23: `binutils` — affected >=0 <2.44-r2
- Alpine:v3.24: `binutils` — affected >=0 <2.44-r2

## Details
A vulnerability has been found in GNU Binutils 2.43/2.44 and classified as problematic. Affected by this vulnerability is the function display_info of the file binutils/bucomm.c of the component objdump. The manipulation leads to memory leak. An attack has to be approached locally. The exploit has been disclosed to the public and may be used. The patch is named ba6ad3a18cb26b79e0e3b84c39f707535bbc344d. It is recommended to apply a patch to fix this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-3198
