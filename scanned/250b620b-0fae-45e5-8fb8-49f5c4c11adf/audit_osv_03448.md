# [H] ALPINE-CVE-2026-14457

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-14457
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-14457
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.8-r0

## Details
Issue summary: In a server or client configuration with RFC7250 Raw Public Keys (RPKs)
enabled, and only the private key (with no associated certificate) configured locally,
a NULL pointer dereference may occur when the remote peer solicits raw public keys and
also sends the typically omitted "signature_algorithms_cert" TLS extension.

Impact summary: The impact is limited to a possible Denial of Service as a result of
an application abort, no data disclosure or remote command execution are possible.

CWE: CWE-476: NULL Pointer Dereference

Description: While a passing comment in sample code in the documentation suggests
that key-only RPK configurations are supported, the best-practice RPK configuration
is to always configure a corresponding certificate (possibly self-signed or
signed by any convenient CA).

When the private key is configured along with a matching certificate, the
"signature_algorithms_cert" extension is handled reliably even without the
fix, and peer clients or servers that don't support raw public keys may be
able to complete a TLS connection by pinning or verifying the corresponding
certificate or its public key.

Deployments that prefer to configure just a private key with no certificate
need to upgrade to an updated release as noted below.

FIPS impact: no

No FIPS modules are affected by this issue, as the SSL protocol implementation
is outside the OpenSSL FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-14457
