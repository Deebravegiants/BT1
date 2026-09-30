# [H] ALPINE-CVE-2026-41564

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-41564
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-41564
Type: osv

## Affected
- Alpine:v3.20: `perl-cryptx` — affected >=0 <0.088-r0
- Alpine:v3.21: `perl-cryptx` — affected >=0 <0.088-r0
- Alpine:v3.22: `perl-cryptx` — affected >=0 <0.088-r0
- Alpine:v3.23: `perl-cryptx` — affected >=0 <0.088-r0
- Alpine:v3.24: `perl-cryptx` — affected >=0 <0.088-r0

## Details
CryptX versions before 0.088 for Perl do not reseed the Crypt::PK PRNG state after forking.

The Crypt::PK::RSA, Crypt::PK::DSA, Crypt::PK::DH, Crypt::PK::ECC, Crypt::PK::Ed25519 and Crypt::PK::X25519 modules seed a per-object PRNG state in their constructors and reuse it without fork detection. A Crypt::PK::* object created before `fork()` shares byte-identical PRNG state with every child process, and any randomized operation they perform can produce identical output, including key generation. Two ECDSA or DSA signatures from different processes are enough to recover the signing private key through nonce-reuse key recovery.

This affects preforking services such as the Starman web server, where a Crypt::PK::* object loaded at startup is inherited by every worker process.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-41564
