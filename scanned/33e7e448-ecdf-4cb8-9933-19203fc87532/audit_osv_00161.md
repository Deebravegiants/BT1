# [H] ALPINE-CVE-2016-6304

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6304
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6304
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.5: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.6: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.7: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.8: `openssl` — affected >=0 <1.0.2i-r0

## Details
Multiple memory leaks in t1_lib.c in OpenSSL before 1.0.1u, 1.0.2 before 1.0.2i, and 1.1.0 before 1.1.0a allow remote attackers to cause a denial of service (memory consumption) via large OCSP Status Request extensions.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6304
