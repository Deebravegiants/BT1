# [H] ALPINE-CVE-2018-7167

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-7167
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7167
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.11: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.12: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.13: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.14: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.15: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.16: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.17: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.18: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.19: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.20: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.21: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.22: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.23: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.24: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.8: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.9: `nodejs` — affected >=0 <8.11.3-r0

## Details
Calling Buffer.fill() or Buffer.alloc() with some parameters can lead to a hang which could result in a Denial of Service. In order to address this vulnerability, the implementations of Buffer.alloc() and Buffer.fill() were updated so that they zero fill instead of hanging in these cases. All versions of Node.js 6.x (LTS "Boron"), 8.x (LTS "Carbon"), and 9.x are vulnerable. All versions of Node.js 10.x (Current) are NOT vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7167
