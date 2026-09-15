# [H] ALPINE-CVE-2025-69420

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-69420
Ecosystem: Alpine:v3.17, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-69420
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=1.1.1 <3.0.19-r0
- Alpine:v3.20: `openssl` — affected >=1.1.1 <3.3.6-r0
- Alpine:v3.21: `openssl` — affected >=1.1.1 <3.3.6-r0
- Alpine:v3.22: `openssl` — affected >=1.1.1 <3.5.5-r0
- Alpine:v3.23: `openssl` — affected >=1.1.1 <3.5.5-r0
- Alpine:v3.24: `openssl` — affected >=1.1.1 <3.5.5-r0

## Details
Issue summary: A type confusion vulnerability exists in the TimeStamp Response
verification code where an ASN1_TYPE union member is accessed without first
validating the type, causing an invalid or NULL pointer dereference when
processing a malformed TimeStamp Response file.

Impact summary: An application calling TS_RESP_verify_response() with a
malformed TimeStamp Response can be caused to dereference an invalid or
NULL pointer when reading, resulting in a Denial of Service.

The functions ossl_ess_get_signing_cert() and ossl_ess_get_signing_cert_v2()
access the signing cert attribute value without validating its type.
When the type is not V_ASN1_SEQUENCE, this results in accessing invalid memory
through the ASN1_TYPE union, causing a crash.

Exploiting this vulnerability requires an attacker to provide a malformed
TimeStamp Response to an application that verifies timestamp responses. The
TimeStamp protocol (RFC 3161) is not widely used and the impact of the
exploit is just a Denial of Service. For these reasons the issue was
assessed as Low severity.

The FIPS modules in 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the TimeStamp Response implementation is outside the OpenSSL FIPS module
boundary.

OpenSSL 3.6, 3.5, 3.4, 3.3, 3.0 and 1.1.1 are vulnerable to this issue.

OpenSSL 1.0.2 is not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-69420
