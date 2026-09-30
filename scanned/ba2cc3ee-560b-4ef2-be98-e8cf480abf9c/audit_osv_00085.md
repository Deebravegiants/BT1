# [H] ALPINE-CVE-2016-2183

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-2183
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-09-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2183
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
The DES and Triple DES ciphers, as used in the TLS, SSH, and IPSec protocols and other protocols and products, have a birthday bound of approximately four billion blocks, which makes it easier for remote attackers to obtain cleartext data via a birthday attack against a long-duration encrypted session, as demonstrated by an HTTPS session using Triple DES in CBC mode, aka a "Sweet32" attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2183
