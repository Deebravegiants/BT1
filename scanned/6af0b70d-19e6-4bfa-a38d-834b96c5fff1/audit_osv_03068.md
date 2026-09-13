# [H] ALPINE-CVE-2024-37370

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-37370
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-37370
Type: osv

## Affected
- Alpine:v3.17: `krb5` — affected >=0 <1.20.2-r1
- Alpine:v3.18: `krb5` — affected >=0 <1.20.2-r1
- Alpine:v3.19: `krb5` — affected >=0 <1.20.3-r0
- Alpine:v3.20: `krb5` — affected >=0 <1.20.3-r0
- Alpine:v3.21: `krb5` — affected >=0 <1.20.3-r0
- Alpine:v3.22: `krb5` — affected >=0 <1.20.3-r0
- Alpine:v3.23: `krb5` — affected >=0 <1.20.3-r0
- Alpine:v3.24: `krb5` — affected >=0 <1.20.3-r0

## Details
In MIT Kerberos 5 (aka krb5) before 1.21.3, an attacker can modify the plaintext Extra Count field of a confidential GSS krb5 wrap token, causing the unwrapped token to appear truncated to the application.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-37370
