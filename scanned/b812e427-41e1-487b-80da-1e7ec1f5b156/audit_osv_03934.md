# [H] ALPINE-CVE-2026-70457

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-70457
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-70457
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=3.2.3 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=3.2.3 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=3.2.3 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=3.2.3 <3.5.0-r0

## Details
rsync 3.2.3 before 3.5.0 contains an out-of-bounds write in parse_size_arg() where the return value of snprintf() is used directly as an index into a .bss-segment array without bounds checking. When snprintf truncates the formatted size string, the return value equals the number of characters that would have been written including the truncated portion, and this value may exceed the array length. The subsequent indexed write targets memory outside the intended array bounds, corrupting .bss memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-70457
