# [M] ALPINE-CVE-2026-22795

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-22795
Ecosystem: Alpine:v3.17, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-22795
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=1.1.1 <3.0.19-r0
- Alpine:v3.20: `openssl` — affected >=1.1.1 <3.3.6-r0
- Alpine:v3.21: `openssl` — affected >=1.1.1 <3.3.6-r0
- Alpine:v3.22: `openssl` — affected >=1.1.1 <3.5.5-r0
- Alpine:v3.23: `openssl` — affected >=1.1.1 <3.5.5-r0
- Alpine:v3.24: `openssl` — affected >=1.1.1 <3.5.5-r0

## Details
Issue summary: An invalid or NULL pointer dereference can happen in
an application processing a malformed PKCS#12 file.

Impact summary: An application processing a malformed PKCS#12 file can be
caused to dereference an invalid or NULL pointer on memory read, resulting
in a Denial of Service.

A type confusion vulnerability exists in PKCS#12 parsing code where
an ASN1_TYPE union member is accessed without first validating the type,
causing an invalid pointer read.

The location is constrained to a 1-byte address space, meaning any
attempted pointer manipulation can only target addresses between 0x00 and 0xFF.
This range corresponds to the zero page, which is unmapped on most modern
operating systems and will reliably result in a crash, leading only to a
Denial of Service. Exploiting this issue also requires a user or application
to process a maliciously crafted PKCS#12 file. It is uncommon to accept
untrusted PKCS#12 files in applications as they are usually used to store
private keys which are trusted by definition. For these reasons, the issue
was assessed as Low severity.

The FIPS modules in 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the PKCS12 implementation is outside the OpenSSL FIPS module boundary.

OpenSSL 3.6, 3.5, 3.4, 3.3, 3.0 and 1.1.1 are vulnerable to this issue.

OpenSSL 1.0.2 is not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-22795
