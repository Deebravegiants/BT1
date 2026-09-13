# [C] ALPINE-CVE-2026-11856

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-11856
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11856
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.10.6 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=7.10.6 <8.21.0-r0

## Details
Successfully using libcurl to do a transfer to a specific HTTP origin
(`hostA`) with **Digest** authentication and then changing the origin to a
different one (`hostB`) for a second transfer, reusing the same handle, makes
libcurl wrongly pass on the  `Authorization:` header field meant for `hostA`,
to `hostB`.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11856
