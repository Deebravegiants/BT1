# [H] `libparsec_crypto` does not check for weak order point of curve 25519

## Summary
Severity: High
Advisory: CVE-2025-62514
Aliases: GHSA-hrc9-gm58-pgj9
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2025-62514
Type: osv

## Details
Parsec is a cloud-based application for cryptographically secure file sharing. In versions on the 3.x branch prior to 3.6.0, `libparsec_crypto`, a component of the Parsec application, does not check for weak order point of Curve25519 when compiled with its RustCrypto backend. In practice this means an attacker in a man-in-the-middle position would be able to provide weak order points to both parties in the Diffie-Hellman exchange, resulting in a high probability to for both parties to obtain the same shared key (hence leading to a successful SAS code exchange, misleading both parties into thinking no MITM has occurred) which is also known by the attacker. Note only Parsec web is impacted (as Parsec desktop uses `libparsec_crypto` with the libsodium backend). Version 3.6.0 of Parsec patches the issue.

## References
- https://github.com/Scille/parsec-cloud/blob/e7c5cdbc4234f606ccf3ab2be7e9edc22db16feb/libparsec/crates/crypto/src/rustcrypto/private.rs#L136-L138
- https://github.com/dalek-cryptography/curve25519-dalek/blob/8c53a8f10b146a2fd65069437e3576e49b390e7a/curve25519-dalek/src/montgomery.rs#L132-L146
- https://github.com/dalek-cryptography/curve25519-dalek/blob/8c53a8f10b146a2fd65069437e3576e49b390e7a/x25519-dalek/src/x25519.rs#L364-L366
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62514.json
- https://github.com/Scille/parsec-cloud/security/advisories/GHSA-hrc9-gm58-pgj9
- https://nvd.nist.gov/vuln/detail/CVE-2025-62514
- https://github.com/Scille/parsec-cloud/commit/197bb6387b49fec872b5e4a04dcdb82b3d2995b2
