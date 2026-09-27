# [H] ALPINE-CVE-2025-5245

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-5245
Ecosystem: Alpine:v3.22
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-5245
Type: osv

## Affected
- Alpine:v3.22: `binutils` — affected >=0 <2.44-r3

## Details
A vulnerability classified as critical has been found in GNU Binutils up to 2.44. This affects the function debug_type_samep of the file /binutils/debug.c of the component objdump. The manipulation leads to memory corruption. Local access is required to approach this attack. The exploit has been disclosed to the public and may be used. It is recommended to apply a patch to fix this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-5245
