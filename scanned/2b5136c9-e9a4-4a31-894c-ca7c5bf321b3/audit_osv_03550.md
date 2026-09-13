# [H] ALPINE-CVE-2026-28388

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-28388
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-28388
Type: osv

## Affected
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.3.7-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.3.7-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.5.6-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.5.6-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.5.6-r0

## Details
Issue summary: When a delta CRL that contains a Delta CRL Indicator extension
is processed a NULL pointer dereference might happen if the required CRL
Number extension is missing.

Impact summary: A NULL pointer dereference can trigger a crash which
leads to a Denial of Service for an application.

When CRL processing and delta CRL processing is enabled during X.509
certificate verification, the delta CRL processing does not check
whether the CRL Number extension is NULL before dereferencing it.
When a malformed delta CRL file is being processed, this parameter
can be NULL, causing a NULL pointer dereference.

Exploiting this issue requires the X509_V_FLAG_USE_DELTAS flag to be enabled in
the verification context, the certificate being verified to contain a
freshestCRL extension or the base CRL to have the EXFLAG_FRESHEST flag set, and
an attacker to provide a malformed CRL to an application that processes it.

The vulnerability is limited to Denial of Service and cannot be escalated to
achieve code execution or memory disclosure. For that reason the issue was
assessed as Low severity according to our Security Policy.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-28388
