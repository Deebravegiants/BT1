# [H] ALPINE-CVE-2019-3823

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-3823
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3823
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.11: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.12: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.13: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.14: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.15: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.16: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.64.0-r0
- Alpine:v3.6: `curl` — affected >=0 <7.61.1-r2
- Alpine:v3.7: `curl` — affected >=0 <7.61.1-r2
- Alpine:v3.8: `curl` — affected >=0 <7.61.1-r2
- Alpine:v3.9: `curl` — affected >=0 <7.64.0-r0

## Details
libcurl versions from 7.34.0 to before 7.64.0 are vulnerable to a heap out-of-bounds read in the code handling the end-of-response for SMTP. If the buffer passed to `smtp_endofresp()` isn't NUL terminated and contains no character ending the parsed number, and `len` is set to 5, then the `strtol()` call reads beyond the allocated buffer. The read contents will not be returned to the caller.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3823
