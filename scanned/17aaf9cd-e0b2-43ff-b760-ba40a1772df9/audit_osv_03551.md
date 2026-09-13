# [H] ALPINE-CVE-2026-28389

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-28389
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-28389
Type: osv

## Affected
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.3.7-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.3.7-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.5.6-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.5.6-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.5.6-r0

## Details
Issue summary: During processing of a crafted CMS EnvelopedData message
with KeyAgreeRecipientInfo a NULL pointer dereference can happen.

Impact summary: Applications that process attacker-controlled CMS data may
crash before authentication or cryptographic operations occur resulting in
Denial of Service.

When a CMS EnvelopedData message that uses KeyAgreeRecipientInfo is
processed, the optional parameters field of KeyEncryptionAlgorithmIdentifier
is examined without checking for its presence. This results in a NULL
pointer dereference if the field is missing.

Applications and services that call CMS_decrypt() on untrusted input
(e.g., S/MIME processing or CMS-based protocols) are vulnerable.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-28389
