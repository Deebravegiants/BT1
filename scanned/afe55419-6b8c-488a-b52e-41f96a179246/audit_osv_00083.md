# [H] ALPINE-CVE-2016-2180

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-2180
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2180
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2h-r2
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2h-r2
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2h-r2
- Alpine:v3.5: `openssl` — affected >=0 <1.0.2h-r2
- Alpine:v3.6: `openssl` — affected >=0 <1.0.2h-r2
- Alpine:v3.7: `openssl` — affected >=0 <1.0.2h-r2
- Alpine:v3.8: `openssl` — affected >=0 <1.0.2h-r2

## Details
The TS_OBJ_print_bio function in crypto/ts/ts_lib.c in the X.509 Public Key Infrastructure Time-Stamp Protocol (TSP) implementation in OpenSSL through 1.0.2h allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted time-stamp file that is mishandled by the "openssl ts" command.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2180
