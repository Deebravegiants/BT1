# [H] Plonky3 MultiField32Challenger: transcript malleability and challenge entropy loss

## Summary
Severity: High
Advisory: GHSA-vj64-rjf3-w3v7
CVE: CVE-2026-46654
CWE: CWE-1240, CWE-345
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-vj64-rjf3-w3v7
Type: github-advisory

## Affected
- crates.io: `p3-challenger` — affected >=0 <0.4.3
- crates.io: `p3-challenger` — affected >=0.5.0 <0.5.3

## Details
### Impact

- **Key**: `challenger/src/multi_field_challenger.rs` | `MultiField32Challenger::duplexing` | `transcript_malleability`
- **Affected files**: `challenger/src/multi_field_challenger.rs`, `field/src/helpers.rs`
- **Violated invariant**: The Fiat-Shamir sponge must bind challenges to the exact sequence of observed field elements. Specifically: (1) absorption must be injective — distinct observation streams must produce distinct sponge states, (2) squeezing must be injective — distinct PF rate cells must yield distinct F challenge sequences, and (3) all bits of each absorbed PF element must influence the sponge state.

- **Exploit scenario**: An attacker controlling prover-side observations can craft distinct transcripts that produce identical challenges, breaking the binding property of Fiat-Shamir. Three independent attack vectors exist:

  1. **Partial-chunk aliasing (absorb)**: `duplexing()` packs `input_buffer.chunks(num_f_elms)` via `reduce_32` (base 2^32) with no length marker and no zeroing of unused rate slots. Observing `[x]` followed by a sample yields the same sponge state as `[x, 0, ..., 0]` (padded to `num_f_elms`) followed by a sample, since `reduce_32` treats missing high limbs identically to explicit zeros. The attacker can extend or truncate the tail of any observation batch without changing future challenges.

  2. **Non-injective squeeze (squeeze)**: `split_32` decomposes each PF rate cell into base-2^64 digits and maps each through `TF::from_u64`, which reduces mod `F::ORDER` (~2^31). Two distinct PF values whose base-2^64 digits differ only in their upper 33 bits produce identical F challenge sequences. This weakens the entropy of sampled challenges and can enable selective forgery when the attacker can influence the sponge state pre-squeeze.

  3. **High-bit truncation (observe Hash/MerkleCap)**: `num_f_elms = PF::bits() / 64` computes the number of F limbs per PF element. For BN254 (254-bit field), this yields 3 limbs covering 192 bits — the top 62 bits of every digest word are silently discarded. An attacker can find two distinct BN254 hash digests that differ only in bits 192–253 and observe them interchangeably without affecting challenges.

- **Evidence**: In `duplexing()`, the absorb path (`reduce_32` with base 2^32) and the squeeze path (`split_32` with base 2^64) use incompatible radices with no length domain separation. `reduce_32` is a plain Horner fold `acc * 2^32 + digit` with no padding or tag, so trailing zeros are free. `split_32` extracts u64 digits and casts each via `TF::from_u64`, which performs modular reduction, collapsing the top bits. The limb count `PF::bits() / 64` is a floor division that silently drops all bits beyond `64 * num_f_elms` for fields whose bit-width is not a multiple of 64.

### Patches

Included in v0.4.3 and v0.5.3

## References
- https://github.com/Plonky3/Plonky3/security/advisories/GHSA-vj64-rjf3-w3v7
- https://nvd.nist.gov/vuln/detail/CVE-2026-46654
- https://github.com/Plonky3/Plonky3
