# [C] Orchard Action circuit soundness failure (under-constrained base in halo2_gadgets) enables counterfeiting within the Orchard pool

## Summary
Severity: Critical
Chain: Zcash
Component: zcash/zcash
Published: 2026-07-19
Source: https://github.com/zcash/zcash/security/advisories/GHSA-ghc3-g8w4-whf9
Type: github-advisory

## Details
### Summary

A critical soundness flaw in the `halo2_gadgets` variable-base scalar-multiplication gadget broke the soundness of the Orchard Action circuit, allowing a malicious prover to produce valid-looking Orchard proofs against an under-constrained base point. Exploitation could have permitted counterfeiting (minting) of funds within the Orchard shielded pool — including double-spending a note under multiple nullifiers, or authorizing spends of other users' notes — with no on-chain trace, because the zero-knowledge property hides the malformed witness.

Zcash's total supply cap and user privacy are **not** compromised: the ZIP 209 "turnstile" bounds Orchard outflows to no more than the value that legitimately entered the pool, so any counterfeit value cannot leave Orchard beyond that limit, and no confidential data is disclosed by the flaw. However, because Orchard transactions are shielded, it is not possible to verify after the fact whether counterfeiting occurred during the exposure window. Remediating that residual uncertainty is the purpose of the NU6.3 (Ironwood) upgrade described below.

The underlying flaw was disclosed for the Zcash Foundation's `zebrad` implementation in [GHSA-ww9q-8r59-xv46](https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-ww9q-8r59-xv46) (CVSS 9.3). This advisory records the corresponding disclosure and remediation for `zcashd`. During the private remediation window, this advisory (`GHSA-ghc3-g8w4-whf9`) was used to coordinate deployment of the mitigation with mining-pool partners and other ecosystem operators.

### The vulnerability

The Orchard Action circuit proves, among other statements, the diversified-address integrity relation `pk_d = [ivk] g_d`, which binds an Action to the correct incoming viewing key. That relation is evaluated with the variable-base scalar-multiplication gadget in `halo2_gadgets` (`ecc::chip::mul`), which uses an incomplete double-and-add loop for efficiency.

The defect was a missing copy constraint on the loop's base point. The incomplete double-and-add loop kept the per-iteration base `(x_p, y_p)` constant across loop rows via the `q_mul_2` constraint, but never tied that base to the *real* base: the coordinates were written with `assign_advice`, and the constancy chain reached neither the doubling-row nor the complete-addition base anchors. A malicious prover could therefore run the incomplete loop against a freely chosen constant `B' != base`, making the gadget compute `[a]·base + [b]·B'` instead of `[scalar]·base`.

With that freedom, a prover can satisfy `pk_d = [ivk] g_d` for arbitrary `(pk_d, g_d, ivk)` triples by solving for a base value that forces the computed result to equal the desired `pk_d`, bypassing the check that normally binds an Action to the key that controls the note:

- **Double-spend within the pool:** choosing an incorrect nullifier key `nk` yields a distinct nullifier for the same note, while the under-constrained base is used to satisfy the integrity check anyway — letting the same note be spent more than once (bounded overall by the turnstile).
- **Spending others' notes:** choosing an alternate spend-validating key `ak` for which the attacker knows the signing key lets them construct and authorize a transaction spending a victim's notes.

The root fix (in `halo2_gadgets`) replaces the first-iteration `assign_advice` calls for the base point with `copy_advice`, introducing a copy constraint that pins the first base value to the correct base; combined with the existing `q_mul_2` equality constraints, this transitively constrains every intermediate base value. Because the Orchard verifying key is pinned to the circuit, deploying the corrected circuit is a consensus-level change.

### Impact

- **Integrity: High.** Minting/double-spending within the Orchard pool (bounded by the ZIP 209 turnstile) and unauthorized spending of other users' Orchard notes.
- **Confidentiality: None.** The zero-knowledge property is preserved; no private information is leaked, and exploitation leaves no distinguishing on-chain signature.
- **Supply cap: Not exceeded.** The turnstile prevents counterfeit value from leaving the Orchard pool beyond legitimate inflows; the 21M ZEC cap is not affected.
- **Residual uncertainty:** because the pool is shielded, the absence of exploitation during the exposure window cannot be independently verified — addressed by NU6.3 (Ironwood).

### Discovery and disclosure

The flaw was privately disclosed to the Zcash Open Development Lab (ZODL) on 2026-05-29 at 23:53 by **Taylor Hornby**, a former security engineer at the Electric Coin Company and an independent security researcher contracted by Shielded Labs to perform vulnerability research on the Orchard protocol. Remediation was coordinated among ZODL, Shielded Labs, and the Zcash Foundation, in coordination with mining pools and other operators, and disclosed publicly for `zebrad` as [GHSA-ww9q-8r59-xv46](https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-ww9q-8r59-xv46).

### Remediation process

Remediation proceeded in three coordinated phases:

**1. Emergency soft fork — temporarily disable Orchard (`zcashd` v6.12.4).**
A time-critical soft fork activating at mainnet block height **3363366** (approximately 02:00 UTC on 2026-06-02) added a consensus rule that temporarily **disables Orchard actions**, removing the ability to create the transactions that could exploit the circuit while the hard-fork fix was finalized and deployed. This release was coordinated with mining-pool partners (the coordination tracked under this advisory) and also bundled several unrelated consensus/DoS fixes shipped in the same window (see *Related advisories*).

**2. NU6.2 hard fork — corrected circuit and Orchard re-enabled (`zcashd` v6.20.0).**
The NU6.2 network upgrade activated at mainnet block height **3364600** (approximately 03:00 UTC on 2026-06-03), immediately after the soft fork. NU6.2 updates the pinned Orchard verifying key to the **corrected circuit** (`halo2_gadgets` 0.5.0 / `orchard` 0.14.0 / `zcash_primitives` 0.28.0), **re-enables** Orchard actions under the fixed circuit, and additionally enforces a strict canonical-length limit on Orchard proofs. `zcashd` v6.20.0 is the final `zcashd` release; the network-level fix required a hard fork because it changes the pinned verifying key.

**3. NU6.3 / Ironwood — seal the old pool, start fresh.**
Because exploitation during the exposure window cannot be ruled out by inspection of a shielded pool, the NU6.3 upgrade ("Ironwood") introduces a **new shielded pool built on the corrected Orchard circuit** and permanently **seals the original Orchard pool as withdraw-only**: after activation, funds can no longer be sent or received *within* the old Orchard pool, and may only exit through a turnstile that enforces that outflows never exceed the value that legitimately entered. This restores every node operator's ability to **independently verify the soundness of Zcash's circulating supply**, bounding any hypothetical pre-fix counterfeit from ever increasing the circulating supply. NU6.3 is scheduled to activate at mainnet block height **3428143** (approximately 12:00 UTC on 2026-07-28).

As part of the preparation for Ironwood, a **formal verification of the Action circuit's soundness** — the very property whose failure caused this vulnerability — is being carried out in the [Lean theorem prover](https://github.com/zcash/ironwood). This is an in-progress effort intended to give machine-checked assurance of the soundness of the Action circuit used by both the Orchard and Ironwood pools ahead of the NU6.3 activation, along with clear documentation of the precise scope of what is and is not formally verified.

NU6.3 is **not** supported by `zcashd`, which has reached End of Life. Its End-of-Support halt was reached on 2026-07-18 at block height 3417100 — every `zcashd` v6.20.0 node has now automatically shut down and refuses to restart. Operators must migrate to the Z3 stack: [Zebra](https://github.com/ZcashFoundation/zebra) (the replacement consensus node, from which NU6.3/Ironwood is deployed) and [Zallet](https://zcash.github.io/zallet/) (the full-node wallet, which supports the `zcashd` `wallet.dat`).

### About Ironwood

Ironwood is the shielded pool activated by the NU6.3 network upgrade. It replaces the original Orchard pool with a pool using the corrected Orchard circuit, and pairs that with sealing the old pool behind a withdraw-only turnstile. The goal is to restore independent verifiability of the circulating supply — allowing node operators to confirm that no more value can leave the legacy pool than provably entered it — while preserving Zcash's shielded-transaction privacy for value held in the new pool. See Shielded Labs' [Ironwood overview](https://shieldedlabs.net/ironwood/) and ZODL's [announcement](https://zodl.com/ironwood-a-new-shielded-pool-for-zcash/) for further detail.

### Affected and fixed versions

| Component | Affected | Fixed |
| --- | --- | --- |
| `halo2_gadgets` | < 0.5.0 | 0.5.0 |
| `orchard` | < 0.14.0 | 0.14.0 |
| `zcash_primitives` | < 0.28.0 | 0.28.0 |
| `zcashd` | < 6.20.0 | 6.20.0 (NU6.2) |
| `zebrad` | < 5.0.0 | 5.0.0 (NU6.2); 4.5.3 shipped the interim soft-fork mitigation |

### Credits

- **Taylor Hornby** — discovery and disclosure (contracted by Shielded Labs).
- **Shielded Labs**, **Zcash Open Development Lab (ZODL)**, and the **Zcash Foundation** — coordinated remediation, with mining-pool partners and ecosystem operators.

### Related advisories

`zcashd` v6.12.4 and v6.20.0 were released alongside remediations for several unrelated consensus and denial-of-service issues disclosed in the same window:

- [GHSA-rpcw-q5mr-gq35](https://github.com/zcash/zcash/security/advisories/GHSA-rpcw-q5mr-gq35) — NU5+ block-body poisoning (root)
- [GHSA-qvwc-hc2r-82qv](https://github.com/zcash/zcash/security/advisories/GHSA-qvwc-hc2r-82qv) — incomplete-fix follow-up (`bad-blk-sigops`)
- [GHSA-wmwc-773c-qcvv](https://github.com/zcash/zcash/security/advisories/GHSA-wmwc-773c-qcvv) — `bad-cb-length` path
- [GHSA-382w-958v-m5jr](https://github.com/zcash/zcash/security/advisories/GHSA-382w-958v-m5jr) — `bad-blk-length` path
- [GHSA-g4x5-crjh-29ff](https://github.com/zcash/zcash/security/advisories/GHSA-g4x5-crjh-29ff) — coinbase shielded value-balance `AbortNode` crash loop
- [GHSA-78pp-mc9g-g4mw](https://github.com/zcash/zcash/security/advisories/GHSA-78pp-mc9g-g4mw) — out-of-range pool-value delta: unbanned peer + disk-replay DoS
- [GHSA-2x4w-pxqw-58v9](https://github.com/zcash/zcash/security/advisories/GHSA-2x4w-pxqw-58v9) — non-canonical Orchard proof length / ZIP 317 fee bypass (also closed by the NU6.2 canonical-length rule)
