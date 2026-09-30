# [H] ALPINE-CVE-2016-2106

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-2106
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2106
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.5: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.6: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.7: `openssl` — affected >=0 <1.0.2h-r0
- Alpine:v3.8: `openssl` — affected >=0 <1.0.2h-r0

## Details
Integer overflow in the EVP_EncryptUpdate function in crypto/evp/evp_enc.c in OpenSSL before 1.0.1t and 1.0.2 before 1.0.2h allows remote attackers to cause a denial of service (heap memory corruption) via a large amount of data.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2106
