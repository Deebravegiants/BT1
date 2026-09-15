# [M] ALPINE-CVE-2026-22796

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-22796
Ecosystem: Alpine:v3.17, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-22796
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.19-r0
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.3.6-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.3.6-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.5.5-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.5.5-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.5.5-r0

## Details
Issue summary: A type confusion vulnerability exists in the signature
verification of signed PKCS#7 data where an ASN1_TYPE union member is
accessed without first validating the type, causing an invalid or NULL
pointer dereference when processing malformed PKCS#7 data.

Impact summary: An application performing signature verification of PKCS#7
data or calling directly the PKCS7_digest_from_attributes() function can be
caused to dereference an invalid or NULL pointer when reading, resulting in
a Denial of Service.

The function PKCS7_digest_from_attributes() accesses the message digest attribute
value without validating its type. When the type is not V_ASN1_OCTET_STRING,
this results in accessing invalid memory through the ASN1_TYPE union, causing
a crash.

Exploiting this vulnerability requires an attacker to provide a malformed
signed PKCS#7 to an application that verifies it. The impact of the
exploit is just a Denial of Service, the PKCS7 API is legacy and applications
should be using the CMS API instead. For these reasons the issue was
assessed as Low severity.

The FIPS modules in 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the PKCS#7 parsing implementation is outside the OpenSSL FIPS module
boundary.

OpenSSL 3.6, 3.5, 3.4, 3.3, 3.0, 1.1.1 and 1.0.2 are vulnerable to this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-22796
