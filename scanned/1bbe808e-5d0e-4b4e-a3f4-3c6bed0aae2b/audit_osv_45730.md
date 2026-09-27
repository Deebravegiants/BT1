# [H] Issue summary: A type confusion vulnerability exists in the TimeStamp Response verification code...

## Summary
Severity: High
Advisory: JLSEC-2026-264
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-264
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=3.5.0+0 <3.5.5+0
- Julia: `Openresty_jll` — affected >=1.19.9+0 <1.29.203+0

## Details
Issue summary: A type confusion vulnerability exists in the TimeStamp Response
verification code where an `ASN1_TYPE` union member is accessed without first
validating the type, causing an invalid or NULL pointer dereference when
processing a malformed TimeStamp Response file.

Impact summary: An application calling `TS_RESP_verify_response()` with a
malformed TimeStamp Response can be caused to dereference an invalid or
NULL pointer when reading, resulting in a Denial of Service.

The functions `ossl_ess_get_signing_cert()` and `ossl_ess_get_signing_cert_v2()`
access the signing cert attribute value without validating its type.
When the type is not `V_ASN1_SEQUENCE`, this results in accessing invalid memory
through the `ASN1_TYPE` union, causing a crash.

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
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://github.com/advisories/GHSA-w42r-ph9f-9x66
- https://github.com/openssl/openssl/commit/27c7012c91cc986a598d7540f3079dfde2416eb9
- https://github.com/openssl/openssl/commit/4e254b48ad93cc092be3dd62d97015f33f73133a
- https://github.com/openssl/openssl/commit/564fd9c73787f25693bf9e75faf7bf6bb1305d4e
- https://github.com/openssl/openssl/commit/5eb0770ffcf11b785cf374ff3c19196245e54f1b
- https://github.com/openssl/openssl/commit/a99349ebfc519999edc50620abe24d599b9eb085
- https://nvd.nist.gov/vuln/detail/CVE-2025-69420
- https://openssl-library.org/news/secadv/20260127.txt
