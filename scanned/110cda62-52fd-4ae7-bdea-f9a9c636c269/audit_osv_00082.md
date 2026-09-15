# [H] ALPINE-CVE-2016-2179

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-2179
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2179
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2h-r3
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2h-r3
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2h-r3
- Alpine:v3.5: `openssl` — affected >=0 <1.0.2h-r3
- Alpine:v3.6: `openssl` — affected >=0 <1.0.2h-r3
- Alpine:v3.7: `openssl` — affected >=0 <1.0.2h-r3
- Alpine:v3.8: `openssl` — affected >=0 <1.0.2h-r3

## Details
The DTLS implementation in OpenSSL before 1.1.0 does not properly restrict the lifetime of queue entries associated with unused out-of-order messages, which allows remote attackers to cause a denial of service (memory consumption) by maintaining many crafted DTLS sessions simultaneously, related to d1_lib.c, statem_dtls.c, statem_lib.c, and statem_srvr.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2179
