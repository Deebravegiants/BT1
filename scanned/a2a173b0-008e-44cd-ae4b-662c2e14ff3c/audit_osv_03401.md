# [H] ALPINE-CVE-2025-9230

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-9230
Ecosystem: Alpine:v3.17, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-9230
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=0 <3.0.19-r0
- Alpine:v3.19: `openssl` — affected >=0 <3.1.8-r1
- Alpine:v3.20: `openssl` — affected >=0 <3.3.5-r0
- Alpine:v3.21: `openssl` — affected >=0 <3.3.5-r0
- Alpine:v3.22: `openssl` — affected >=0 <3.5.4-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.4-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.4-r0

## Details
Issue summary: An application trying to decrypt CMS messages encrypted using
password based encryption can trigger an out-of-bounds read and write.

Impact summary: This out-of-bounds read may trigger a crash which leads to
Denial of Service for an application. The out-of-bounds write can cause
a memory corruption which can have various consequences including
a Denial of Service or Execution of attacker-supplied code.

Although the consequences of a successful exploit of this vulnerability
could be severe, the probability that the attacker would be able to
perform it is low. Besides, password based (PWRI) encryption support in CMS
messages is very rarely used. For that reason the issue was assessed as
Moderate severity according to our Security Policy.

The FIPS modules in 3.5, 3.4, 3.3, 3.2, 3.1 and 3.0 are not affected by this
issue, as the CMS implementation is outside the OpenSSL FIPS module
boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-9230
