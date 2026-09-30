# [H] ALPINE-CVE-2025-69421

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-69421
Ecosystem: Alpine:v3.17, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-69421
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.19-r0
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.3.6-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.3.6-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.5.5-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.5.5-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.5.5-r0

## Details
Issue summary: Processing a malformed PKCS#12 file can trigger a NULL pointer
dereference in the PKCS12_item_decrypt_d2i_ex() function.

Impact summary: A NULL pointer dereference can trigger a crash which leads to
Denial of Service for an application processing PKCS#12 files.

The PKCS12_item_decrypt_d2i_ex() function does not check whether the oct
parameter is NULL before dereferencing it. When called from
PKCS12_unpack_p7encdata() with a malformed PKCS#12 file, this parameter can
be NULL, causing a crash. The vulnerability is limited to Denial of Service
and cannot be escalated to achieve code execution or memory disclosure.

Exploiting this issue requires an attacker to provide a malformed PKCS#12 file
to an application that processes it. For that reason the issue was assessed as
Low severity according to our Security Policy.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the PKCS#12 implementation is outside the OpenSSL FIPS module boundary.

OpenSSL 3.6, 3.5, 3.4, 3.3, 3.0, 1.1.1 and 1.0.2 are vulnerable to this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-69421
