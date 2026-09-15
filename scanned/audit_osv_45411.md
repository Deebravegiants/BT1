# [H] Issue Summary: The PKCS#12 file processing fails to perform sufficient input validation for files...

## Summary
Severity: High
Advisory: JLSEC-2026-1134
Ecosystem: Julia
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1134
Type: osv

## Affected
- Julia: `AppBundler` — affected >=1.0.0 <1.0.1
- Julia: `OpenSSL_jll` — affected >=3.5.0+0 <3.5.7+0
- Julia: `Openresty_jll` — affected >=1.29.203+0

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
- https://github.com/advisories/GHSA-4jgc-cj59-f9mm
- https://github.com/openssl/openssl/commit/0300eb9ddce7a0895bf301a4b0c03a9da2313a0f
- https://github.com/openssl/openssl/commit/79eb76a937e474bb7610a0a3dc57131dc8dc6610
- https://github.com/openssl/openssl/commit/85dcbb3abaa4878af5c8fbbe11bce708fcf984a7
- https://github.com/openssl/openssl/commit/ec36f2417c4ddd8cabce4b4a60a3d7a7365f2d81
- https://github.com/openssl/security/commit/0300eb9ddce7a0895bf301a4b0c03a9da2313a0f
- https://github.com/openssl/security/commit/79eb76a937e474bb7610a0a3dc57131dc8dc6610
- https://github.com/openssl/security/commit/85dcbb3abaa4878af5c8fbbe11bce708fcf984a7
- https://github.com/openssl/security/commit/ec36f2417c4ddd8cabce4b4a60a3d7a7365f2d81
- https://nvd.nist.gov/vuln/detail/CVE-2026-34181
- https://openssl-library.org/news/secadv/20260609.txt
