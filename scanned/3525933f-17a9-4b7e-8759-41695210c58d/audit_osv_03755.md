# [H] ALPINE-CVE-2026-45447

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-45447
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-45447
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.5.7-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.5.7-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.5.7-r0

## Details
Issue summary: A specially crafted PKCS#7 or S/MIME signed message could
trigger a use-after-free during PKCS#7 signature verification.

Impact summary: A use-after-free may result in process crashes, heap
corruption, or potentially remote code execution.

When processing a PKCS#7 or S/MIME signed message, if the SignedData
digestAlgorithms field is present as an empty ASN.1 SET, OpenSSL may
incorrectly free a caller-owned BIO during PKCS7_verify(). A subsequent
use of the BIO by the calling application results in a use-after-free
condition.

In the common case this occurs when the application later calls
BIO_free() on the BIO originally passed to PKCS7_verify(). Depending
on allocator behavior and application-specific BIO usage patterns, this
may result in a crash or other memory corruption. In some application
contexts this may potentially be exploitable for remote code execution.

Applications that process PKCS#7 or S/MIME signed messages using OpenSSL
PKCS#7 APIs may be affected. Applications using the CMS APIs for this
processing are not affected.

The FIPS modules in 4.0, 3.6, 3.5, 3.4, and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-45447
