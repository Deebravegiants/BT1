# [M] ALPINE-CVE-2018-0733

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-0733
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-0733
Type: osv

## Affected
- Alpine:v3.3: `openssl` — affected >=1.1.0 <1.0.2o-r0
- Alpine:v3.4: `openssl` — affected >=1.1.0 <1.0.2o-r0
- Alpine:v3.5: `openssl` — affected >=1.1.0 <1.0.2o-r0
- Alpine:v3.6: `openssl` — affected >=1.1.0 <1.0.2o-r0
- Alpine:v3.7: `openssl` — affected >=1.1.0 <1.0.2o-r0
- Alpine:v3.8: `openssl` — affected >=1.1.0 <1.0.2o-r0

## Details
Because of an implementation bug the PA-RISC CRYPTO_memcmp function is effectively reduced to only comparing the least significant bit of each byte. This allows an attacker to forge messages that would be considered as authenticated in an amount of tries lower than that guaranteed by the security claims of the scheme. The module can only be compiled by the HP-UX assembler, so that only HP-UX PA-RISC targets are affected. Fixed in OpenSSL 1.1.0h (Affected 1.1.0-1.1.0g).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-0733
