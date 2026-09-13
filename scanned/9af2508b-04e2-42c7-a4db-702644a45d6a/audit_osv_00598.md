# [M] ALPINE-CVE-2017-18018

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-18018
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-01-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-18018
Type: osv

## Affected
- Alpine:v3.10: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.11: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.12: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.13: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.14: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.15: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.16: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.17: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.18: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.19: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.20: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.21: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.22: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.23: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.24: `coreutils` — affected >=0 <8.30-r0
- Alpine:v3.7: `coreutils` — affected >=0 <8.28-r0
- Alpine:v3.8: `coreutils` — affected >=0 <8.29-r2
- Alpine:v3.9: `coreutils` — affected >=0 <8.30-r0

## Details
In GNU Coreutils through 8.29, chown-core.c in chown and chgrp does not prevent replacement of a plain file with a symlink during use of the POSIX "-R -L" options, which allows local users to modify the ownership of arbitrary files by leveraging a race condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-18018
