# [M] ALPINE-CVE-2025-40918

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-40918
Ecosystem: Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-40918
Type: osv

## Affected
- Alpine:v3.24: `perl-authen-sasl` — affected >=0 <2.1900

## Details
Authen::SASL::Perl::DIGEST_MD5 versions 2.04 through 2.1800 for Perl generates the cnonce insecurely.

The cnonce (client nonce) is generated from an MD5 hash of the PID, the epoch time and the built-in rand function. The PID will come from a small set of numbers, and the epoch time may be guessed, if it is not leaked from the HTTP Date header. The built-in rand function is unsuitable for cryptographic usage.

According to RFC 2831, The cnonce-value is an opaque quoted string value provided by the client and used by both client and server to avoid chosen plaintext attacks, and to provide mutual authentication. The security of the implementation
 depends on a good choice. It is RECOMMENDED that it contain at least 64 bits of entropy.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-40918
