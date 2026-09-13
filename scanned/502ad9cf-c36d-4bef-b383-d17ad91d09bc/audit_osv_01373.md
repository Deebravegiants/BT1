# [C] ALPINE-CVE-2019-12450

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-12450
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12450
Type: osv

## Affected
- Alpine:v3.10: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.11: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.12: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.13: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.14: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.15: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.16: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.17: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.18: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.19: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.20: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.21: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.22: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.23: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.24: `glib` — affected >=2.15.0 <2.60.4-r0
- Alpine:v3.7: `glib` — affected >=2.15.0 <2.54.2-r1
- Alpine:v3.8: `glib` — affected >=2.15.0 <2.56.1-r1
- Alpine:v3.9: `glib` — affected >=2.15.0 <2.58.1-r3

## Details
file_copy_fallback in gio/gfile.c in GNOME GLib 2.15.0 through 2.61.1 does not properly restrict file permissions while a copy operation is in progress. Instead, default permissions are used.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12450
