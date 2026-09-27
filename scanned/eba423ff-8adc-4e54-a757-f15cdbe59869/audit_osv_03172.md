# [M] ALPINE-CVE-2024-9143

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-9143
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-10-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-9143
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=0 <3.0.15-r1
- Alpine:v3.18: `openssl` — affected >=0 <3.1.7-r1
- Alpine:v3.19: `openssl` — affected >=0 <3.1.7-r1
- Alpine:v3.20: `openssl` — affected >=0 <3.3.2-r1
- Alpine:v3.21: `openssl` — affected >=0 <3.3.2-r3
- Alpine:v3.22: `openssl` — affected >=0 <3.3.2-r3
- Alpine:v3.23: `openssl` — affected >=0 <3.3.2-r3
- Alpine:v3.24: `openssl` — affected >=0 <3.3.2-r3

## Details
Issue summary: Use of the low-level GF(2^m) elliptic curve APIs with untrusted
explicit values for the field polynomial can lead to out-of-bounds memory reads
or writes.

Impact summary: Out of bound memory writes can lead to an application crash or
even a possibility of a remote code execution, however, in all the protocols
involving Elliptic Curve Cryptography that we're aware of, either only "named
curves" are supported, or, if explicit curve parameters are supported, they
specify an X9.62 encoding of binary (GF(2^m)) curves that can't represent
problematic input values. Thus the likelihood of existence of a vulnerable
application is low.

In particular, the X9.62 encoding is used for ECC keys in X.509 certificates,
so problematic inputs cannot occur in the context of processing X.509
certificates.  Any problematic use-cases would have to be using an "exotic"
curve encoding.

The affected APIs include: EC_GROUP_new_curve_GF2m(), EC_GROUP_new_from_params(),
and various supporting BN_GF2m_*() functions.

Applications working with "exotic" explicit binary (GF(2^m)) curve parameters,
that make it possible to represent invalid field polynomials with a zero
constant term, via the above or similar APIs, may terminate abruptly as a
result of reading or writing outside of array bounds.  Remote code execution
cannot easily be ruled out.

The FIPS modules in 3.3, 3.2, 3.1 and 3.0 are not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-9143
