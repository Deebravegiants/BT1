# [M] ALPINE-CVE-2025-4575

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-4575
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-05-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-4575
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=0 <3.5.1-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.1-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.1-r0

## Details
Issue summary: Use of -addreject option with the openssl x509 application adds
a trusted use instead of a rejected use for a certificate.

Impact summary: If a user intends to make a trusted certificate rejected for
a particular use it will be instead marked as trusted for that use.

A copy & paste error during minor refactoring of the code introduced this
issue in the OpenSSL 3.5 version. If, for example, a trusted CA certificate
should be trusted only for the purpose of authenticating TLS servers but not
for CMS signature verification and the CMS signature verification is intended
to be marked as rejected with the -addreject option, the resulting CA
certificate will be trusted for CMS signature verification purpose instead.

Only users which use the trusted certificate format who use the openssl x509
command line application to add rejected uses are affected by this issue.
The issues affecting only the command line application are considered to
be Low severity.

The FIPS modules in 3.5, 3.4, 3.3, 3.2, 3.1 and 3.0 are not affected by this
issue.

OpenSSL 3.4, 3.3, 3.2, 3.1, 3.0, 1.1.1 and 1.0.2 are also not affected by this
issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-4575
