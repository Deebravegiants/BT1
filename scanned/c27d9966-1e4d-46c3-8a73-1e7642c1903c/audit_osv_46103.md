# [M] Generating the ECDSA nonce k samples a random number r and then truncates this randomness with a...

## Summary
Severity: Medium
Advisory: JLSEC-2026-682
Ecosystem: Julia
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-682
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
Generating the ECDSA nonce k samples a random number r and then
truncates this randomness with a modular reduction mod n where n is the
order of the elliptic curve. Meaning k = r mod n. The division used
during the reduction estimates a factor `q_e` by dividing the upper two
digits (a digit having e.g. a size of 8 byte) of r by the upper digit of
n and then decrements `q_e` in a loop until it has the correct size.
Observing the number of times `q_e` is decremented through a control-flow
revealing side-channel reveals a bias in the most significant bits of
k. Depending on the curve this is either a negligible bias or a
significant bias large enough to reconstruct k with lattice reduction
methods. For SECP160R1, e.g., we find a bias of 15 bits.

## References
- https://github.com/advisories/GHSA-grjj-54gm-q5vf
- https://github.com/wolfSSL/wolfssl/pull/7020
- https://github.com/wolfSSL/wolfssl/releases/tag/v5.7.2-stable
- https://nvd.nist.gov/vuln/detail/CVE-2024-1544
