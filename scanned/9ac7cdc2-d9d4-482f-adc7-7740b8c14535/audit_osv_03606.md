# [C] ALPINE-CVE-2026-3381

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-3381
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-3381
Type: osv

## Affected
- Alpine:v3.20: `perl-compress-raw-zlib` — affected >=0 <2.222-r0
- Alpine:v3.21: `perl-compress-raw-zlib` — affected >=0 <2.222-r0
- Alpine:v3.22: `perl-compress-raw-zlib` — affected >=0 <2.222-r0
- Alpine:v3.23: `perl-compress-raw-zlib` — affected >=0 <2.222-r0
- Alpine:v3.24: `perl-compress-raw-zlib` — affected >=0 <2.222-r0

## Details
Compress::Raw::Zlib versions through 2.219 for Perl use potentially insecure versions of zlib.

Compress::Raw::Zlib includes a copy of the zlib library. Compress::Raw::Zlib version 2.220 includes zlib 1.3.2, which addresses findings fron the 7ASecurity audit of zlib. The includes fixs for CVE-2026-27171.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-3381
