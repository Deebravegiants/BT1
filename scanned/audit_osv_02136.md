# [H] ALPINE-CVE-2021-27219

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-27219
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-27219
Type: osv

## Affected
- Alpine:v3.13: `glib` — affected >=2.67.0 <2.66.6-r0
- Alpine:v3.14: `glib` — affected >=2.67.0 <2.66.6-r0
- Alpine:v3.15: `glib` — affected >=2.67.0 <2.66.6-r0
- Alpine:v3.16: `glib` — affected >=2.67.0 <2.66.6-r0
- Alpine:v3.17: `glib` — affected >=2.67.0 <2.66.6-r0
- Alpine:v3.18: `glib` — affected >=2.67.0 <2.66.6-r0
- Alpine:v3.19: `glib` — affected >=2.67.0 <2.66.6-r0
- Alpine:v3.20: `glib` — affected >=2.67.0 <2.66.6-r0
- Alpine:v3.21: `glib` — affected >=2.67.0 <2.66.6-r0
- Alpine:v3.22: `glib` — affected >=2.67.0 <2.66.6-r0
- Alpine:v3.23: `glib` — affected >=2.67.0 <2.66.6-r0
- Alpine:v3.24: `glib` — affected >=2.67.0 <2.66.6-r0

## Details
An issue was discovered in GNOME GLib before 2.66.6 and 2.67.x before 2.67.3. The function g_bytes_new has an integer overflow on 64-bit platforms due to an implicit cast from 64 bits to 32 bits. The overflow could potentially lead to memory corruption.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-27219
