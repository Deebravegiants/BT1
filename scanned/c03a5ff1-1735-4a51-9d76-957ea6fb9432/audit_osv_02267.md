# [H] ALPINE-CVE-2021-3712

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3712
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3712
Type: osv

## Affected
- Alpine:v3.11: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.12: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.13: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.14: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.17: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.18: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.19: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.20: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <1.1.1l-r0
- Alpine:v3.15: `openssl3` — affected >=0 <1.1.1l-r0
- Alpine:v3.16: `openssl3` — affected >=0 <1.1.1l-r0

## Details
ASN.1 strings are represented internally within OpenSSL as an ASN1_STRING structure which contains a buffer holding the string data and a field holding the buffer length. This contrasts with normal C strings which are repesented as a buffer for the string data which is terminated with a NUL (0) byte. Although not a strict requirement, ASN.1 strings that are parsed using OpenSSL's own "d2i" functions (and other similar parsing functions) as well as any string whose value has been set with the ASN1_STRING_set() function will additionally NUL terminate the byte array in the ASN1_STRING structure. However, it is possible for applications to directly construct valid ASN1_STRING structures which do not NUL terminate the byte array by directly setting the "data" and "length" fields in the ASN1_STRING array. This can also happen by using the ASN1_STRING_set0() function. Numerous OpenSSL functions that print ASN.1 data have been found to assume that the ASN1_STRING byte array will be NUL terminated, even though this is not guaranteed for strings that have been directly constructed. Where an application requests an ASN.1 structure to be printed, and where that ASN.1 structure contains ASN1_STRINGs that have been directly constructed by the application without NUL terminating the "data" field, then a read buffer overrun can occur. The same thing can also occur during name constraints processing of certificates (for example if a certificate has been directly constructed by the application instead of loading it via the OpenSSL parsing functions, and the certificate contains non NUL terminated ASN1_STRING structures). It can also occur in the X509_get1_email(), X509_REQ_get1_email() and X509_get1_ocsp() functions. If a malicious actor can cause an application to directly construct an ASN1_STRING and then process it through one of the affected OpenSSL functions then this issue could be hit. This might result in a crash (causing a Denial of Service attack). It could also result in the disclosure of private memory contents (such as private keys, or sensitive plaintext). Fixed in OpenSSL 1.1.1l (Affected 1.1.1-1.1.1k). Fixed in OpenSSL 1.0.2za (Affected 1.0.2-1.0.2y).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3712
