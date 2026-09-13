# [M] ALPINE-CVE-2026-26007

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-26007
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-26007
Type: osv

## Affected
- Alpine:v3.23: `py3-cryptography` — affected >=0 <46.0.5-r0
- Alpine:v3.24: `py3-cryptography` — affected >=0 <46.0.5-r0

## Details
cryptography is a package designed to expose cryptographic primitives and recipes to Python developers. Prior to 46.0.5, the public_key_from_numbers (or EllipticCurvePublicNumbers.public_key()), EllipticCurvePublicNumbers.public_key(), load_der_public_key() and load_pem_public_key() functions do not verify that the point belongs to the expected prime-order subgroup of the curve. This missing validation allows an attacker to provide a public key point P from a small-order subgroup. This can lead to security issues in various situations, such as the most commonly used signature verification (ECDSA) and shared key negotiation (ECDH). When the victim computes the shared secret as S = [victim_private_key]P via ECDH, this leaks information about victim_private_key mod (small_subgroup_order). For curves with cofactor > 1, this reveals the least significant bits of the private key. When these weak public keys are used in ECDSA , it's easy to forge signatures on the small subgroup. Only SECT curves are impacted by this. This vulnerability is fixed in 46.0.5.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-26007
