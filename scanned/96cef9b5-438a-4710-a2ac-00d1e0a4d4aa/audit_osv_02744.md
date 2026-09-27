# [H] ALPINE-CVE-2023-0286

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-0286
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-02-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-0286
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
There is a type confusion vulnerability relating to X.400 address processing
inside an X.509 GeneralName. X.400 addresses were parsed as an ASN1_STRING but
the public structure definition for GENERAL_NAME incorrectly specified the type
of the x400Address field as ASN1_TYPE. This field is subsequently interpreted by
the OpenSSL function GENERAL_NAME_cmp as an ASN1_TYPE rather than an
ASN1_STRING.

When CRL checking is enabled (i.e. the application sets the
X509_V_FLAG_CRL_CHECK flag), this vulnerability may allow an attacker to pass
arbitrary pointers to a memcmp call, enabling them to read memory contents or
enact a denial of service. In most cases, the attack requires the attacker to
provide both the certificate chain and CRL, neither of which need to have a
valid signature. If the attacker only controls one of these inputs, the other
input must already contain an X.400 address as a CRL distribution point, which
is uncommon. As such, this vulnerability is most likely to only affect
applications which have implemented their own functionality for retrieving CRLs
over a network.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-0286
