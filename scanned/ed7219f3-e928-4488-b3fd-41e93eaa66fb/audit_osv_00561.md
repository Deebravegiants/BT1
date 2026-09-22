# [C] ALPINE-CVE-2017-15896

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-15896
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15896
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.11: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.12: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.13: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.14: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.15: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.16: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.17: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.18: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.19: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.20: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.21: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.22: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.23: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.24: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.7: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.8: `nodejs` — affected >=0 <8.9.3-r0
- Alpine:v3.9: `nodejs` — affected >=0 <8.9.3-r0

## Details
Node.js was affected by OpenSSL vulnerability CVE-2017-3737 in regards to the use of SSL_read() due to TLS handshake failure. The result was that an active network attacker could send application data to Node.js using the TLS or HTTP2 modules in a way that bypassed TLS authentication and encryption.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15896
