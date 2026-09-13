# [M] ALPINE-CVE-2025-9820

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-9820
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-9820
Type: osv

## Affected
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.11-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.11-r0

## Details
A flaw was found in the GnuTLS library, specifically in the gnutls_pkcs11_token_init() function that handles PKCS#11 token initialization. When a token label longer than expected is processed, the function writes past the end of a fixed-size stack buffer. This programming error can cause the application using GnuTLS to crash or, in certain conditions, be exploited for code execution. As a result, systems or applications relying on GnuTLS may be vulnerable to a denial of service or local privilege escalation attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-9820
