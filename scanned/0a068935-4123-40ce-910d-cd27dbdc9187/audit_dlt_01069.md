# [H] Poseidon V1 variable-length input collision via implicit zero-padding

## Summary
Severity: High
Chain: soroban-poseidon
Component: soroban-poseidon
CVE: CVE-2026-32129
CWE: Use of Weak Hash
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-g2p6-hh5v-7hfm
Type: github-advisory

## Details
## Impact

Poseidon V1 (`PoseidonSponge`) accepts variable-length inputs without injective padding. When a caller provides fewer inputs than the sponge rate (`inputs.len() < T - 1`), unused rate positions are implicitly zero-filled. This allows trivial hash collisions: for any input vector `[m1, ..., mk]` hashed with a sponge of rate > k, `hash([m1, ..., mk])` equals `hash([m1, ..., mk, 0])` because both produce identical pre-permutation states.

This affects any use of `PoseidonSponge` or `poseidon_hash` where the number of inputs is less than `T - 1` (e.g., hashing 1 input with `T=3`).

Poseidon2 (`Poseidon2Sponge`) is **not affected** — it encodes the input length in the capacity element (`IV = input_len << 64`), making different-length inputs produce distinct states.

## Patches

Fixed by enforcing `inputs.len() == RATE` in `PoseidonSponge::compute_hash`, matching circom's invariant that `nInputs` always equals `T - 1`. Users should upgrade to the next release containing this fix.

## Workarounds

If upgrading is not immediately possible:

- Ensure callers **always** use `T = inputs.len() + 1` (full-rate), which is how circom uses Poseidon. For example, to hash 2 inputs, use `T=3`; to hash 1 input, use `T=2`. Never use a sponge with more rate capacity than the number of inputs.
- Alternatively, migrate to `Poseidon2Sponge`, which is safe for variable-length inputs due to its length-encoding IV.

## References
- [circom Poseidon implementation](https://github.com/iden3/circomlib/blob/master/circuits/poseidon.circom) — reference implementation where `nInputs` determines `T`
- [Poseidon paper](https://eprint.iacr.org/2019/458) — Section 4 discusses sponge construction and padding requirements
