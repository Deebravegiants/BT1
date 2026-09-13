# [H] ALPINE-CVE-2026-1145

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-1145
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-1145
Type: osv

## Affected
- Alpine:v3.23: `quickjs-ng` — affected >=0 <0.11.0-r1
- Alpine:v3.24: `quickjs-ng` — affected >=0 <0.11.0-r2

## Details
A flaw has been found in quickjs-ng quickjs up to 0.11.0. Affected by this vulnerability is the function js_typed_array_constructor_ta of the file quickjs.c. This manipulation causes heap-based buffer overflow. The attack is possible to be carried out remotely. The exploit has been published and may be used. Patch name: 53aebe66170d545bb6265906fe4324e4477de8b4. It is suggested to install a patch to address this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-1145
