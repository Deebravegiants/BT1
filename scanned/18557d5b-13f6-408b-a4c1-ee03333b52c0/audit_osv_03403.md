# [M] ALPINE-CVE-2025-9232

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-9232
Ecosystem: Alpine:v3.17, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-9232
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=0 <3.0.19-r0
- Alpine:v3.19: `openssl` — affected >=0 <3.1.8-r1
- Alpine:v3.20: `openssl` — affected >=0 <3.3.5-r0
- Alpine:v3.21: `openssl` — affected >=0 <3.3.5-r0
- Alpine:v3.22: `openssl` — affected >=0 <3.5.4-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.4-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.4-r0

## Details
Issue summary: An application using the OpenSSL HTTP client API functions may
trigger an out-of-bounds read if the 'no_proxy' environment variable is set and
the host portion of the authority component of the HTTP URL is an IPv6 address.

Impact summary: An out-of-bounds read can trigger a crash which leads to
Denial of Service for an application.

The OpenSSL HTTP client API functions can be used directly by applications
but they are also used by the OCSP client functions and CMP (Certificate
Management Protocol) client implementation in OpenSSL. However the URLs used
by these implementations are unlikely to be controlled by an attacker.

In this vulnerable code the out of bounds read can only trigger a crash.
Furthermore the vulnerability requires an attacker-controlled URL to be
passed from an application to the OpenSSL function and the user has to have
a 'no_proxy' environment variable set. For the aforementioned reasons the
issue was assessed as Low severity.

The vulnerable code was introduced in the following patch releases:
3.0.16, 3.1.8, 3.2.4, 3.3.3, 3.4.0 and 3.5.0.

The FIPS modules in 3.5, 3.4, 3.3, 3.2, 3.1 and 3.0 are not affected by this
issue, as the HTTP client implementation is outside the OpenSSL FIPS module
boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-9232
