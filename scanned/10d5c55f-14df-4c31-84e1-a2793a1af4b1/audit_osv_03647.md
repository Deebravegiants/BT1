# [M] ALPINE-CVE-2026-39314

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-39314
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-39314
Type: osv

## Affected
- Alpine:v3.20: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.21: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.22: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.23: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.24: `cups` — affected >=0 <2.4.18-r0

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.16 and prior, an integer underflow vulnerability in _ppdCreateFromIPP() (cups/ppd-cache.c) allows any unprivileged local user to crash the cupsd root process by supplying a negative job-password-supported IPP attribute. The bounds check only caps the upper bound, so a negative value passes validation, is cast to size_t (wrapping to ~2^64), and is used as the length argument to memset() on a 33-byte stack buffer. This causes an immediate SIGSEGV in the cupsd root process. Combined with systemd's Restart=on-failure, an attacker can repeat the crash for sustained denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-39314
