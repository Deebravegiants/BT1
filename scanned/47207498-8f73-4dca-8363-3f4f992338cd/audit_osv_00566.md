# [H] ALPINE-CVE-2017-16544

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-16544
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-16544
Type: osv

## Affected
- Alpine:v3.10: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.11: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.12: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.13: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.14: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.15: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.16: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.17: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.18: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.19: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.20: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.21: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.22: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.23: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.24: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.3: `busybox` — affected >=0 <1.24.2-r2
- Alpine:v3.4: `busybox` — affected >=0 <1.24.2-r13
- Alpine:v3.5: `busybox` — affected >=0 <1.25.1-r1
- Alpine:v3.6: `busybox` — affected >=0 <1.26.2-r9
- Alpine:v3.7: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.8: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.9: `busybox` — affected >=0 <1.27.2-r4

## Details
In the add_match function in libbb/lineedit.c in BusyBox through 1.27.2, the tab autocomplete feature of the shell, used to get a list of filenames in a directory, does not sanitize filenames and results in executing any escape sequence in the terminal. This could potentially result in code execution, arbitrary file writes, or other attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-16544
