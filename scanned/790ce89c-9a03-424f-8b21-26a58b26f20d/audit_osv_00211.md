# [H] ALPINE-CVE-2016-7052

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-7052
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7052
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2j-r0
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2j-r0
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2j-r0

## Details
crypto/x509/x509_vfy.c in OpenSSL 1.0.2i allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) by triggering a CRL operation.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7052
