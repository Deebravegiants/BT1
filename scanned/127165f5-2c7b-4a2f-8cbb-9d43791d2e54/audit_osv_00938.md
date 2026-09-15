# [H] ALPINE-CVE-2018-12115

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-12115
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12115
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.11: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.12: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.13: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.14: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.15: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.16: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.17: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.18: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.19: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.20: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.21: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.22: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.23: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.24: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.8: `nodejs` — affected >=0 <8.11.4-r0
- Alpine:v3.9: `nodejs` — affected >=0 <8.11.4-r0

## Details
In all versions of Node.js prior to 6.14.4, 8.11.4 and 10.9.0 when used with UCS-2 encoding (recognized by Node.js under the names `'ucs2'`, `'ucs-2'`, `'utf16le'` and `'utf-16le'`), `Buffer#write()` can be abused to write outside of the bounds of a single `Buffer`. Writes that start from the second-to-last position of a buffer cause a miscalculation of the maximum length of the input bytes to be written.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12115
