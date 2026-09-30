# [H] ALPINE-CVE-2016-6302

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6302
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6302
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
The tls_decrypt_ticket function in ssl/t1_lib.c in OpenSSL before 1.1.0 does not consider the HMAC size during validation of the ticket length, which allows remote attackers to cause a denial of service via a ticket that is too short.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6302
