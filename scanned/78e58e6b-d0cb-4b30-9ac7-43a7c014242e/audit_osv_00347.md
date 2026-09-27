# [H] ALPINE-CVE-2017-0379

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-0379
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-0379
Type: osv

## Affected
- Alpine:v3.4: `libgcrypt` — affected >=0 <1.7.9-r0
- Alpine:v3.5: `libgcrypt` — affected >=0 <1.7.9-r0
- Alpine:v3.6: `libgcrypt` — affected >=0 <1.7.9-r0

## Details
Libgcrypt before 1.8.1 does not properly consider Curve25519 side-channel attacks, which makes it easier for attackers to discover a secret key, related to cipher/ecc.c and mpi/ec.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-0379
