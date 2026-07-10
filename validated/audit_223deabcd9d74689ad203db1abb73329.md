### Title
Governance Threshold Substituted for Domain Reconstruction Threshold in Robust-ECDSA Presignature Generation - (`File: crates/node/src/providers/robust_ecdsa/presign.rs`)

### Summary

The `compute_thresholds` function and `run_presignature_generation_follower` in the robust-ECDSA (DamgardEtAl) presignature pipeline both use the global **governance threshold** (`mpc_config.participants.threshold`) in place of the **domain-specific reconstruction threshold** when computing the `MaxMalicious` security parameter and selecting the number of signers. This is the direct analog of the EIP-2981 bug: a constant/wrong value is substituted for the actual per-domain value in a critical calculation, causing the system to enforce a stricter (and incorrect) threshold than the domain requires.

### Finding Description

In `crates/node/src/providers/robust_ecdsa/presign.rs`, the leader path calls:

```rust
let (num_signers, robust_ecdsa_threshold) = compute_thresholds(
    mpc_config.participants.threshold,   // ← governance threshold, not domain reconstruction threshold
    running_participants.len(),
)
``` [1](#0-0) 

The `compute_thresholds` function itself carries an explicit acknowledgement of the substitution:

```rust
/// TODO(#3164): once the node supports per-domain thresholds, this should
/// take the domain-specific threshold instead of the single governance threshold.
fn compute_thresholds(
    governance_threshold: u64,
    ...
``` [2](#0-1) 

The follower path makes the identical substitution:

```rust
let threshold = self.mpc_config.participants.threshold.try_into()?;
let robust_ecdsa_threshold = translate_threshold(threshold, number_of_participants)?;
``` [3](#0-2) 

`translate_threshold` converts the threshold into `MaxMalicious::from((number_of_signers - 1) / 2)`, which is the Byzantine-fault tolerance parameter for the robust-ECDSA protocol. [4](#0-3) 

The contract enforces `governance_threshold >= max(reconstruction_threshold)` across all domains: [5](#0-4) 

So whenever a DamgardEtAl domain is configured with `reconstruction_threshold < governance_threshold` (a valid and expected multi-domain configuration), the node selects `governance_threshold` signers and computes `MaxMalicious` from that inflated value instead of from the domain's actual `reconstruction_threshold`.

### Impact Explanation

**Medium.** This breaks the request-lifecycle invariant for DamgardEtAl (robust-ECDSA) signing domains. The invariant is: *a domain with reconstruction threshold `t` must be able to produce signatures whenever `t` participants are online.* Because the node uses `governance_threshold` (which is ≥ `reconstruction_threshold`) as the signer count, presignature generation requires `governance_threshold` participants to be simultaneously reachable. When `reconstruction_threshold ≤ online_participants < governance_threshold`, presignature generation stalls, the presignature buffer drains, and all pending signing requests for that domain time out and are dropped. This is a production safety invariant violation in the request lifecycle that does not require network-level DoS or operator misconfiguration — it is triggered by any valid deployment where the two thresholds differ.

### Likelihood Explanation

The contract explicitly permits and enforces `governance_threshold ≥ max(reconstruction_threshold)`, so any multi-domain deployment that sets a DamgardEtAl domain's `reconstruction_threshold` below the governance threshold (a normal and expected configuration) will exhibit this bug continuously. The TODO comment at the root cause confirms the developers are aware the current code is incorrect.

### Recommendation

Pass the domain-specific `reconstruction_threshold` (from `DomainConfig::reconstruction_threshold`) into `compute_thresholds` and `run_presignature_generation_follower` instead of `mpc_config.participants.threshold`. The design document already describes the correct approach:

```rust
// Proposed (clean):
let dk = distributed_key_registry.get(distributed_key_id);
let threshold = dk.reconstruction_threshold;
``` [6](#0-5) 

### Proof of Concept

1. Deploy a contract with 10 participants, `governance_threshold = 7`, and one DamgardEtAl domain with `reconstruction_threshold = 5`.
2. Bring 6 participants online (satisfies `reconstruction_threshold = 5`, does not satisfy `governance_threshold = 7`).
3. Submit a signing request for the DamgardEtAl domain.
4. Observe: `run_background_presignature_generation` calls `compute_thresholds(7, 10)`, selects 7 signers via `select_random_active_participants_including_me(7, ...)`, but only 6 are reachable. Presignature generation fails to gather enough participants, the presignature buffer stays empty, and the signing request times out — even though the domain's own reconstruction threshold of 5 is fully satisfied. [7](#0-6)

### Citations

**File:** crates/node/src/providers/robust_ecdsa/presign.rs (L83-94)
```rust
    let running_participants: Vec<_> = mpc_config
        .participants
        .participants
        .iter()
        .map(|p| p.id)
        .collect();

    let (num_signers, robust_ecdsa_threshold) = compute_thresholds(
        mpc_config.participants.threshold,
        running_participants.len(),
    )
    .expect("invalid governance threshold for robust-ECDSA");
```

**File:** crates/node/src/providers/robust_ecdsa/presign.rs (L183-196)
```rust
/// Computes `(num_signers, robust_ecdsa_threshold)` and validates the
/// `2 * max_malicious + 1 <= num_signers` invariant. Returns an error only if
/// the configured governance threshold is invalid for robust-ECDSA.
///
/// TODO(#3164): once the node supports per-domain thresholds, this should
/// take the domain-specific threshold instead of the single governance threshold.
fn compute_thresholds(
    governance_threshold: u64,
    num_running_participants: usize,
) -> anyhow::Result<(usize, MaxMalicious)> {
    let governance_threshold: usize = governance_threshold.try_into()?;
    let num_signers = get_number_of_signers(governance_threshold, num_running_participants)?;
    let robust_ecdsa_threshold =
        translate_threshold(governance_threshold, num_running_participants)?;
```

**File:** crates/node/src/providers/robust_ecdsa/presign.rs (L217-219)
```rust
        let number_of_participants = self.mpc_config.participants.participants.len();
        let threshold = self.mpc_config.participants.threshold.try_into()?;
        let robust_ecdsa_threshold = translate_threshold(threshold, number_of_participants)?;
```

**File:** crates/node/src/providers/robust_ecdsa.rs (L280-290)
```rust
pub(super) fn translate_threshold(
    threshold: usize,
    number_of_participants: usize,
) -> anyhow::Result<MaxMalicious> {
    let number_of_signers = get_number_of_signers(threshold, number_of_participants)?;
    anyhow::ensure!(
        number_of_signers >= 5,
        "Robust ECDSA requires the threshold to be at least 2, which implies that the number of signers needs to be at least 5"
    );
    Ok(MaxMalicious::from((number_of_signers - 1) / 2))
}
```

**File:** crates/contract/src/primitives/thresholds.rs (L92-107)
```rust
    pub fn validate_governance_against_reconstruction(
        num_participants: u64,
        governance: Threshold,
        max_reconstruction_threshold: Option<ReconstructionThreshold>,
    ) -> Result<(), Error> {
        Self::validate_threshold(num_participants, governance)?;
        if let Some(max_reconstruction_threshold) = max_reconstruction_threshold
            && governance.value() < max_reconstruction_threshold.inner()
        {
            return Err(InvalidThreshold::BelowReconstructionThreshold {
                reconstruction_threshold: max_reconstruction_threshold.inner(),
                governance_threshold: governance.value(),
            }
            .into());
        }
        Ok(())
```

**File:** docs/design/domain-separation.md (L912-927)
```markdown
```rust
// Current (hack):
let threshold: usize = mpc_config.participants.threshold.try_into()?;
let threshold = ReconstructionThreshold::from(threshold);

// Proposed (clean):
let dk = distributed_key_registry.get(distributed_key_id);
let active_signers = min_active_participants(&dk.protocol, &dk.reconstruction_threshold);
let threshold = match dk.protocol {
    Protocol::DamgardEtAl => {
        let max_malicious = MaxMalicious::from(dk.reconstruction_threshold.inner() - 1);
        // Use MaxMalicious directly, no translation needed
    }
    _ => ReconstructionThreshold::from(dk.reconstruction_threshold.inner()),
};
```
```
