# [H] Soundness issue with Plonky2 look up tables

## Summary
Severity: High
Chain: ZK
Component: 0xPolygonZero/plonky2
CVE: CVE-2025-24802
CWE: Use of a Cryptographic Primitive with a Risky Implementation
Published: 2025-01-30
Source: https://github.com/0xPolygonZero/plonky2/security/advisories/GHSA-hj49-h7fq-px5h
Type: github-advisory

## Details
### Impact
Lookup tables, whose length is not divisible by `26 = floor(num_routed_wires / 3)` always include the `0 -> 0` input-output pair. Thus a malicious prover can always prove that `f(0) = 0` for any lookup table f (unless its length happens to be divisible by 26).

The cause of problem is that the `LookupTableGate`-s are [padded with zeros](https://github.com/0xPolygonZero/plonky2/blob/main/plonky2/src/plonk/prover.rs#L97).

The fix is done by padding with an existing table pair, similarly to `LookupGate`.

A workaround from the user side is to extend the table (by repeating some entries) so that its length becomes divisible by 26.

Fortunately, the seemingly most common use case, namely, hash functions with table-based sbox-es, are not vulnerable:

* both Monolith's and Tip5/Tip4's s-box tables already map 0 to 0;
* more generally, forcing several (0,0) pairs inside such a hash function appears to be a too strong restriction to find an otherwise valid trace.

A malicious prover exploiting this could cheat a circuit which statement is the following:
- output `x + f(x)` for some private input `x`, where `f(x) := 100 - x` is implemented by a lookup table.

A malicious prover would be able to convince an honest verifier that they know an `0 <= x < 64` such that `x + (100 - x) = 0`.

### Patches
Yes, upgrade to v1.0.1

### Workarounds
No

### References
