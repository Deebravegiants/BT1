# [H] ALPINE-CVE-2026-34181

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-34181
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34181
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=3.4.0 <3.5.7-r0
- Alpine:v3.23: `openssl` — affected >=3.4.0 <3.5.7-r0
- Alpine:v3.24: `openssl` — affected >=3.4.0 <3.5.7-r0

## Details
Issue Summary: The PKCS#12 file processing fails to perform sufficient input
validation for files that use Password-Based Message Authentication Code 1
(PBMAC1) integrity mechanism allowing a certificate and private key forgery.

Impact Summary: An attacker impersonating a user can cause a service reading
PKCS#12 files to accept forged certificates and private keys with a 1 in 256
probability.

If a service accepting PKCS#12 files is using passwords for authenticating
the received files, the attacker can create unencrypted PKCS#12 files that
use PBMAC1 authentication that specifies an HMAC key of only one byte, allowing
them to craft a file that will be accepted with a 1 in 256 probability.
That would then cause the service to accept a certificate and private key
controlled by the attacker.

The FIPS modules are not affected by this issue, as the affected code is
outside the OpenSSL FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34181
