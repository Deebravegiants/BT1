# [H] ALPINE-CVE-2023-5363

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-5363
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-5363
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.12-r0
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.1.4-r0
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.1.4-r0
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.1.4-r0
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.1.4-r0
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.1.4-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.1.4-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.1.4-r0

## Details
Issue summary: A bug has been identified in the processing of key and
initialisation vector (IV) lengths.  This can lead to potential truncation
or overruns during the initialisation of some symmetric ciphers.

Impact summary: A truncation in the IV can result in non-uniqueness,
which could result in loss of confidentiality for some cipher modes.

When calling EVP_EncryptInit_ex2(), EVP_DecryptInit_ex2() or
EVP_CipherInit_ex2() the provided OSSL_PARAM array is processed after
the key and IV have been established.  Any alterations to the key length,
via the "keylen" parameter or the IV length, via the "ivlen" parameter,
within the OSSL_PARAM array will not take effect as intended, potentially
causing truncation or overreading of these values.  The following ciphers
and cipher modes are impacted: RC2, RC4, RC5, CCM, GCM and OCB.

For the CCM, GCM and OCB cipher modes, truncation of the IV can result in
loss of confidentiality.  For example, when following NIST's SP 800-38D
section 8.2.1 guidance for constructing a deterministic IV for AES in
GCM mode, truncation of the counter portion could lead to IV reuse.

Both truncations and overruns of the key and overruns of the IV will
produce incorrect results and could, in some cases, trigger a memory
exception.  However, these issues are not currently assessed as security
critical.

Changing the key and/or IV lengths is not considered to be a common operation
and the vulnerable API was recently introduced. Furthermore it is likely that
application developers will have spotted this problem during testing since
decryption would fail unless both peers in the communication were similarly
vulnerable. For these reasons we expect the probability of an application being
vulnerable to this to be quite low. However if an application is vulnerable then
this issue is considered very serious. For these reasons we have assessed this
issue as Moderate severity overall.

The OpenSSL SSL/TLS implementation is not affected by this issue.

The OpenSSL 3.0 and 3.1 FIPS providers are not affected by this because
the issue lies outside of the FIPS provider boundary.

OpenSSL 3.1 and 3.0 are vulnerable to this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-5363
