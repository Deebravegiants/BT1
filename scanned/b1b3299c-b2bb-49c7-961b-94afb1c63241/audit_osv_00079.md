# [H] ALPINE-CVE-2016-2176

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-2176
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2016-05-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2176
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
The X509_NAME_oneline function in crypto/x509/x509_obj.c in OpenSSL before 1.0.1t and 1.0.2 before 1.0.2h allows remote attackers to obtain sensitive information from process stack memory or cause a denial of service (buffer over-read) via crafted EBCDIC ASN.1 data.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2176
