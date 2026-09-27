# [H] ALPINE-CVE-2023-0464

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-0464
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-0464
Type: osv

## Affected
- Alpine:v3.14: `openssl` — affected >=1.0.2 <1.1.1t-r1
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1t-r2
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1t-r1
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.8-r1
- Alpine:v3.18: `openssl` — affected >=1.0.2 <3.1.0-r1
- Alpine:v3.19: `openssl` — affected >=1.0.2 <3.1.0-r1
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.1.0-r1
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.1.0-r1
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.1.0-r1
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.1.0-r1
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.1.0-r1
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.8-r1
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.8-r1

## Details
A security vulnerability has been identified in all supported versions

of OpenSSL related to the verification of X.509 certificate chains
that include policy constraints.  Attackers may be able to exploit this
vulnerability by creating a malicious certificate chain that triggers
exponential use of computational resources, leading to a denial-of-service
(DoS) attack on affected systems.

Policy processing is disabled by default but can be enabled by passing
the `-policy' argument to the command line utilities or by calling the
`X509_VERIFY_PARAM_set1_policies()' function.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-0464
