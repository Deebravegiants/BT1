# [C] Missing copy constraint in halo2_gadgets variable-base scalar multiplication allows under-constrained base, breaking Orchard Action circuit soundness

## Summary
Severity: Critical
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-54496
CWE: Insufficient Verification of Data Authenticity
Published: 2026-06-15
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-ww9q-8r59-xv46
Type: github-advisory

## Details
### Summary

A soundness vulnerability in the variable-base scalar multiplication gadget of `halo2_gadgets` allowed a malicious prover to produce a valid proof for an Orchard Action with an *under-constrained* base point. Because this gadget enforces the diversified-address-integrity condition of the Orchard Action statement, the flaw let a prover satisfy that condition for an arbitrary (pk<sub>d</sub>, g<sub>d</sub>, ivk) triple, effectively bypassing the check that binds an Action to the correct incoming viewing key — and therefore to the correct nullifier (nf) and spend validating key (ak) — of the note being spent.

The main practical consequence is that an adversary could have performed a **double-spend within the Orchard pool**, resulting in a balance violation: the same note could be spent multiple times, each time revealing a distinct, valid-looking nullifier. The total ZEC supply was protected by Zcash's turnstile mechanism, which bounds value flowing out of any pool, so unbounded inflation of the overall supply was not possible; the exposure was inflation of value *within* the Orchard pool up to the turnstile-enforced limit.

Exploiting the vulnerability via a double-spend is **undetectable on-chain**. Exploitation only requires setting private circuit inputs to chosen values, and nullifiers produced by a double-spend are indistinguishable from honest nullifiers, so the zero-knowledge property hides any signature of the attack.

Alternatively, an adversary could (before the fix) have **stolen funds** by forging a spend authorization for an existing note. To do so they would have to know the note plaintext, which in practice they might obtain by knowing the corresponding incoming viewing key. For example, this could be used to bypass the protection provided by holding spending keys on a hardware wallet, if the linked software wallet were compromised. This form of exploitation cannot be detected via the turnstile (which might be a motivation to exploit the vulnerability in this way rather than via balance violation). It can be detected by the legitimate holder of stolen funds being unable to spend them, or by seeing the note's nullifier on-chain — but this cannot necessarily be distinguished from compromise of the spending key by other means.

The vulnerability has existed since the Orchard pool was introduced in the NU5 network upgrade (activated May 31, 2022). There is no evidence it was exploited prior to remediation.

Note that use of the vulnerability, either for balance violation or for theft of funds, would need to have occurred before it was remediated. Theft would be in principle detectable from that point (since the real nullifier would appear on-chain). Balance violation would not be detectable at the point of exploitation.

### Root cause

The defect is in the double-and-add implementation of variable-base scalar multiplication in `halo2_gadgets/src/ecc/chip/mul/incomplete.rs`. For performance, the algorithm uses incomplete point-addition formulas in its intermediate stage. (Incomplete addition is safe here in principle: the first and last stages use complete addition, and reaching a degenerate case would require breaking discrete log.)

The base point is fed into the incomplete-addition stage via `assign_advice()`, which assigns a witness value (a private circuit input) **without** introducing a constraint that ties that value to the actual base the algorithm is supposed to operate on:

```rust
region.assign_advice(|| "x_p", self.double_and_add.x_p, row + offset, || x_p)?;
region.assign_advice(|| "y_p", self.y_p, row + offset, || y_p)?;
```
*(`halo2_gadgets/src/ecc/chip/mul/incomplete.rs`, around L309–L310 at commit `32a87582dfb0ad9364ef3ffe71751ceab2a502ea`.)*

The existing `q_mul_2` constraint forces the base values used *across* the incomplete-addition loop to be equal to one another, but nothing forces them to equal the **actual base**. A malicious prover therefore has complete freedom to choose the base used by the loop. Given target pk<sub>d</sub>, g<sub>d</sub>, and ivk, the prover can solve for the base value that makes the computed [ivk] g<sub>d</sub> equal the desired pk<sub>d</sub>, satisfying the diversified-address-integrity equation pk<sub>d</sub><sup>old</sup> = [ivk] g<sub>d</sub><sup>old</sup> for inputs that an honest prover could never satisfy.

### Why this enables a double-spend

The Orchard Action statement constrains the nullifier of the spent note to be derived from the correct nullifier key nk, which in turn is bound to the correct incoming viewing key ivk, via ivk = Commit<sup>ivk</sup><sub>rivk</sub>(Extract<sub>ℙ</sub>(ak<sup>ℙ</sup>), nk). The diversified-address-integrity check pk<sub>d</sub> = [ivk] g<sub>d</sub> is what normally guarantees the prover used the correct ivk —and hence the correct nk— for the note. With that check bypassable:

1. The prover picks a fresh, **incorrect** nk for the note being spent. Since nk feeds the nullifier computation, a wrong nk yields a different nullifier for the same note.
2. Other circuit constraints still force the prover to derive ivk honestly from that wrong nk, producing a wrong ivk for the note — which would normally be caught by the integrity check.
3. The prover uses the under-constrained base to satisfy pk<sub>d</sub> = [ivk] g<sub>d</sub> anyway, defeating the check.
4. Each distinct wrong nk produces a distinct valid nullifier, allowing the note to be spent repeatedly.

### Why this enables theft

The spend validating key, ak<sup>ℙ</sup> (essentially equivalent to ak), is also constrained via ivk = Commit<sup>ivk</sup><sub>rivk</sub>(Extract<sub>ℙ</sub>(ak<sup>ℙ</sup>), nk). As above, the diversified-address-integrity check is what normally guarantees the prover used the correct ivk —and hence the correct ak— for the note. With that check bypassable:

1. The prover picks an ak for which they know the private key, ask.
2. They construct a transaction that spends the victim's notes, and sign it using that ask.

### Impact

- **Integrity:** High. A malicious prover could spend Orchard notes multiple times, inflating value within the Orchard pool. This is bounded only by the turnstile limit on the pool. Alternatively, the prover could authorize spending other users' notes without having the spending key.
- **Confidentiality:** None. The zero-knowledge property is intact; no private data is disclosed. This is also why the attack leaves no observable on-chain signature.
- **Availability:** Not directly affected by the bug. (The coordinated response temporarily disabled Orchard actions as a mitigation; that was an operational choice, not an effect of the vulnerability.) On the other hand, either theft of funds, or inability to spend funds due to a future turnstile violation could be considered an availability consequence.

### Affected versions

- `halo2_gadgets` `< 0.5.0`
- `orchard` `< 0.14.0`
- `zcash_primitives` `< 0.28.0`
- `zcashd` `< 6.20.0`
- `zebrad` `< 5.0.0`

### Patches

The circuit-level fix replaces the first-iteration `assign_advice()` calls for the base point with `copy_advice()`, introducing a copy constraint that requires the first base value to equal the correct base. Combined with the existing `q_mul_2` equality constraint across the loop, this transitively constrains every base value in the incomplete-addition stage to the correct base, closing the freedom the attacker relied on.

Because remediating a zero-knowledge circuit changes the pinned verifying key, the network-level fix required a hard fork (NU6.2). NU6.2 re-enables Orchard with the corrected circuit and routes Orchard proofs to a per-circuit verifying key (`InsecurePreNu6_2` / `FixedPostNu6_2`).

- `halo2_gadgets` 0.5.0
- `orchard` 0.14.0
- `zcash_primitives` 0.28.0
- `zebrad` 5.0.0 (NU6.2); 4.5.3 ships the interim soft-fork mitigation
-  `zcashd` 6.20.0 (NU6.2)

### Workarounds / mitigations

There is no client-side workaround for the underlying soundness flaw short of the circuit fix. The deployed interim mitigation (Zebra 4.5.3 / equivalent) was a soft fork that rejected all Orchard-containing transactions and blocks, fully neutralizing exploitation until NU6.2 activated.

Downstream projects that depend on the affected crates should:

- Upgrade `halo2_gadgets`, `orchard`, and `zcash_primitives` to the patched versions above.
- Audit any other use of `assign_advice()` (and similar non-constraining assignment APIs) where the intended invariant is that a witnessed value equals a known/fixed value; such sites should use `copy_advice()` (or otherwise enforce an explicit constraint).

### Indicators / detection

Exploitation produces no distinguishing on-chain signature. The turnstile mechanism, which tracks total ZEC across all value pools, provides a ground-truth supply check and confirmed the total supply remained intact. Heuristic analysis of Orchard transaction arity (e.g. patterns of duplicate-then-consolidate behavior) is possible but inconclusive against normal shielded-activity variance.

### Timeline (MDT)

| Date / Time | Event |
|---|---|
| 2022-05-31 11:50 | Vulnerable NU5 upgrade activates (bug introduced) |
| 2026-05-29 (evening) | Vulnerability discovered during a protocol audit |
| 2026-05-29 23:53 | Responsibly disclosed to ZODL core engineers |
| 2026-05-30 06:30 | Disclosure acknowledged by ZODL |
| 2026-06-01 (~21:30) | Emergency soft-fork mitigation activated (block 3,363,426) |
| 2026-06-03 00:05 EDT | NU6.2 hard fork activates, Orchard re-enabled with fix (block 3,364,600) |

### Credits

Discovered and responsibly disclosed by **Taylor Hornby**, independent security researcher, during a protocol audit conducted on behalf of **Shielded Labs**. Analysis and remediation was led by ZODL engineers **Jack Grigg**, **Daira-Emma Hopwood**, and **Kris Nuttycombe**, with Zebra patch work by **Arya Solhi** (Zcash Foundation).

### References

- Zcash Foundation: *Zebra 4.5.3 and 5.0.0: Emergency Soft Fork and NU6.2 Activation* — https://zfnd.org/zebra-4-5-3-and-5-0-0-emergency-soft-fork-and-nu6-2-activation/
- Affected source (pre-fix): `halo2_gadgets/src/ecc/chip/mul/incomplete.rs` @ commit `32a87582dfb0ad9364ef3ffe71751ceab2a502ea`, L309–L310
