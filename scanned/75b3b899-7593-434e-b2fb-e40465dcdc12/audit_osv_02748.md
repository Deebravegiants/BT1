# [M] ALPINE-CVE-2023-0465

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-0465
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-03-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-0465
Type: osv

## Affected
- Alpine:v3.14: `openssl` — affected >=1.0.2 <1.1.1t-r2
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1t-r2
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1t-r2
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.8-r2
- Alpine:v3.18: `openssl` — affected >=1.0.2 <3.1.0-r2
- Alpine:v3.19: `openssl` — affected >=1.0.2 <3.1.0-r2
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.1.0-r2
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.1.0-r2
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.1.0-r2
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.1.0-r2
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.1.0-r2
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.8-r2
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.8-r2

## Details
Applications that use a non-default option when verifying certificates may be
vulnerable to an attack from a malicious CA to circumvent certain checks.

Invalid certificate policies in leaf certificates are silently ignored by
OpenSSL and other certificate policy checks are skipped for that certificate.
A malicious CA could use this to deliberately assert invalid certificate policies
in order to circumvent policy checking on the certificate altogether.

Policy processing is disabled by default but can be enabled by passing
the `-policy' argument to the command line utilities or by calling the
`X509_VERIFY_PARAM_set1_policies()' function.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-0465
