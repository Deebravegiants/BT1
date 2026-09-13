# [H] ALPINE-CVE-2021-27218

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-27218
Ecosystem: Alpine:v3.13
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-27218
Type: osv

## Affected
- Alpine:v3.13: `glib` — affected >=2.67.0 <2.66.7-r0

## Details
An issue was discovered in GNOME GLib before 2.66.7 and 2.67.x before 2.67.4. If g_byte_array_new_take() was called with a buffer of 4GB or more on a 64-bit platform, the length would be truncated modulo 2**32, causing unintended length truncation.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-27218
