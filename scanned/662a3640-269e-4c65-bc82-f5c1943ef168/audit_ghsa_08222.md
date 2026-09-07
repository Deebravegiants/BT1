# [H]  libcrux-ml-dsa: Signature Verification on AVX2 Platforms Mishandles Edge Case

## Summary
Severity: High
Advisory: GHSA-fhvh-vw7h-9xf3
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-fhvh-vw7h-9xf3
Type: github-advisory

## Affected
- crates.io: `libcrux-ml-dsa` — affected >=0 <0.0.9

## Details
The AVX2 implementation of ML-DSA verification incorrectly implemented
the `use_hint` function, mishandling an edge case that should lead to
signature rejection.

## Impact
An attacker could make the ML-DSA verifier accept a crafted invalid
signature under a maliciously generated verification key, if the AVX2
implementation is used.

## Mitigation
From version `0.0.9` the edge case is handled correctly and invalid
signatures are rejected.

## References
- https://github.com/C2SP/wycheproof/pull/234
- https://github.com/cryspen/libcrux/pull/1398
- https://github.com/tink-crypto/tink-go/pull/48
- https://github.com/cryspen/libcrux
- https://rustsec.org/advisories/RUSTSEC-2026-0125.html
