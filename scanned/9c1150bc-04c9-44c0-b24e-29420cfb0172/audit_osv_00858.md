# [M] ALPINE-CVE-2018-0739

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-0739
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-0739
Type: osv

## Affected
- Alpine:v3.3: `openssl` — affected >=1.0.2b <1.0.2o-r0
- Alpine:v3.4: `openssl` — affected >=1.0.2b <1.0.2o-r0
- Alpine:v3.5: `openssl` — affected >=1.0.2b <1.0.2o-r0
- Alpine:v3.6: `openssl` — affected >=1.0.2b <1.0.2o-r0
- Alpine:v3.7: `openssl` — affected >=1.0.2b <1.0.2o-r0
- Alpine:v3.8: `openssl` — affected >=1.0.2b <1.0.2o-r0

## Details
Constructed ASN.1 types with a recursive definition (such as can be found in PKCS7) could eventually exceed the stack given malicious input with excessive recursion. This could result in a Denial Of Service attack. There are no such structures used within SSL/TLS that come from untrusted sources so this is considered safe. Fixed in OpenSSL 1.1.0h (Affected 1.1.0-1.1.0g). Fixed in OpenSSL 1.0.2o (Affected 1.0.2b-1.0.2n).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-0739
