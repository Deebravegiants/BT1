# [H] ALPINE-CVE-2023-0215

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-0215
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-0215
Type: osv

## Affected
- Alpine:v3.14: `openssl` — affected >=1.0.2 <1.1.1t-r0
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1t-r0
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1t-r0
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.18: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.19: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.0.8-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.8-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.8-r0

## Details
The public API function BIO_new_NDEF is a helper function used for streaming
ASN.1 data via a BIO. It is primarily used internally to OpenSSL to support the
SMIME, CMS and PKCS7 streaming capabilities, but may also be called directly by
end user applications.

The function receives a BIO from the caller, prepends a new BIO_f_asn1 filter
BIO onto the front of it to form a BIO chain, and then returns the new head of
the BIO chain to the caller. Under certain conditions, for example if a CMS
recipient public key is invalid, the new filter BIO is freed and the function
returns a NULL result indicating a failure. However, in this case, the BIO chain
is not properly cleaned up and the BIO passed by the caller still retains
internal pointers to the previously freed filter BIO. If the caller then goes on
to call BIO_pop() on the BIO then a use-after-free will occur. This will most
likely result in a crash.



This scenario occurs directly in the internal function B64_write_ASN1() which
may cause BIO_new_NDEF() to be called and will subsequently call BIO_pop() on
the BIO. This internal function is in turn called by the public API functions
PEM_write_bio_ASN1_stream, PEM_write_bio_CMS_stream, PEM_write_bio_PKCS7_stream,
SMIME_write_ASN1, SMIME_write_CMS and SMIME_write_PKCS7.

Other public API functions that may be impacted by this include
i2d_ASN1_bio_stream, BIO_new_CMS, BIO_new_PKCS7, i2d_CMS_bio_stream and
i2d_PKCS7_bio_stream.

The OpenSSL cms and smime command line applications are similarly affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-0215
