### Title
Wrong Threshold Used in `recompute_available_foreign_chains` for DamgardEtAl Protocol - (File: `crates/contract/src/lib.rs`)

---

### Summary

`recompute_available_foreign_chains` uses `reconstruction_threshold` (t) directly as the minimum supporter count for marking a foreign chain as "available." For the `DamgardEtAl` protocol, the actual required active signers is `2t − 1` (honest-majority requirement). A chain can therefore be incorrectly marked available when only `t` participants cover it, while `2t − 1` are needed to produce a valid signature — the same class of wrong-unit comparison as the reference report.

---

### Finding Description

In `recompute_available_foreign_chains` the threshold passed to `update_available_chains_config_cache` is derived as:

```rust
// TODO(#3556): replace this with a per-scheme
// `required_active_signers(protocol, reconstruction_threshold)`.
let Some(threshold) = self.protocol_state.domain_registry().ok().and_then(|r| {
    r.domains()
        .iter()
        .filter(|d| d.purpose == DomainPurpose::ForeignTx)
        .map(|d| d.reconstruction_threshold.inner())   // raw t
        .max()
}) else { ... };
``` [1](#0-0) 

`reconstruction_threshold.inner()` returns the raw `t`. For `DamgardEtAl`, the protocol requires an honest majority: `2t − 1 ≤ n`. This is validated at domain-creation time:

```rust
if domain.protocol == Protocol::DamgardEtAl {
    let required = t.checked_mul(2).and_then(|x| x.checked_sub(1))...;
    if required > num_participants { return Err(...); }
}
``` [2](#0-1) 

So the protocol itself knows `2t − 1` participants are needed to reconstruct the key, but `recompute_available_foreign_chains` only requires `t` supporters before marking a chain available. `update_available_chains_config_cache` then applies:

```rust
.filter_map(|(chain, count)| (count >= threshold).then_some(chain))
``` [3](#0-2) 

For `DamgardEtAl` with `reconstruction_threshold = t`, a chain is marked available when `count ≥ t`, but the MPC network actually needs `count ≥ 2t − 1` to sign. The TODO comment in the source explicitly acknowledges this gap and names the missing helper (`required_active_signers(protocol, reconstruction_threshold)`). [4](#0-3) 

The parallel to the reference report is direct: `totalSupply()` (shares) was compared against `globalLendLimit` (assets) without conversion; here `reconstruction_threshold` (t) is compared against the supporter count without converting to `required_active_signers` (2t − 1 for DamgardEtAl).

---

### Impact Explanation

When a `ForeignTx` domain uses `DamgardEtAl` with `reconstruction_threshold = t`:

- `verify_foreign_transaction` **accepts** requests for a chain that has `t` to `2t − 2` supporters, because `get_available_foreign_chains` incorrectly reports it as available.
- The MPC network **cannot complete** those requests: only `t` participants cover the chain, but `2t − 1` are required to reconstruct the DamgardEtAl key share.
- Every accepted request times out, permanently consuming the user's gas and leaving the cross-chain operation in a failed state.

This breaks the production safety invariant stated in the design documentation: *"a request is accepted only when C is available (≥ signing_threshold participants cover it), so an accepted request can reach the signing threshold."* [5](#0-4) 

The impact class is **Medium**: request-lifecycle manipulation that breaks a production safety/accounting invariant (accepted requests that cannot be fulfilled) without requiring network-level DoS or operator misconfiguration.

---

### Likelihood Explanation

The attacker-controlled entry path is `verify_foreign_transaction` — an unprivileged, publicly callable contract method. Any user can submit a foreign-chain transaction request. The precondition is that a `ForeignTx` domain using `DamgardEtAl` exists and that between `t` and `2t − 2` participants have registered coverage for the target chain. The TODO comment (`#3556`) confirms the team is aware the current code is incorrect for `DamgardEtAl` and has not yet fixed it. If `DamgardEtAl` is or becomes permitted for `ForeignTx` domains (the `validate_domain_purpose` implementation was not fully inspectable in this review), the bug is directly reachable.

---

### Recommendation

Replace the direct use of `reconstruction_threshold.inner()` with a protocol-aware helper:

```rust
fn required_active_signers(protocol: Protocol, t: u64) -> u64 {
    match protocol {
        Protocol::DamgardEtAl => 2 * t - 1,
        _ => t,
    }
}
```

Then in `recompute_available_foreign_chains`:

```rust
.map(|d| required_active_signers(d.protocol, d.reconstruction_threshold.inner()))
.max()
```

This mirrors the fix in the reference report: convert the raw stored value to the semantically correct unit before comparing against the limit.

---

### Proof of Concept

1. Register a `ForeignTx` domain with `Protocol::DamgardEtAl` and `reconstruction_threshold = 3` (so `required_active_signers = 5`).
2. Have exactly 3 of 7 participants call `register_foreign_chains_config` reporting coverage for Bitcoin.
3. `recompute_available_foreign_chains` computes `threshold = 3`, counts 3 supporters, and marks Bitcoin available (`3 ≥ 3`).
4. A user calls `verify_foreign_transaction` targeting Bitcoin — the contract accepts it because `get_available_foreign_chains()` includes Bitcoin.
5. The MPC nodes attempt to sign: only 3 participants cover Bitcoin, but DamgardEtAl requires `2×3 − 1 = 5`. No valid signature is produced.
6. The yield-resume promise times out; the user's request is permanently lost with no recourse. [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L1028-1055)
```rust
    fn recompute_available_foreign_chains(&mut self) {
        let Ok(params) = self.protocol_state.threshold_parameters() else {
            return;
        };
        // TODO(#3556): replace this with a per-scheme
        // `required_active_signers(protocol, reconstruction_threshold)`.
        let Some(threshold) = self.protocol_state.domain_registry().ok().and_then(|r| {
            r.domains()
                .iter()
                .filter(|d| d.purpose == DomainPurpose::ForeignTx)
                .map(|d| d.reconstruction_threshold.inner())
                .max()
        }) else {
            // No op if contract isn't in Running or Resharing state, or
            // there is no foreign tx domain registered.
            // Not panicking is intentional.
            log!("Skipping available foreign chains recomputation");
            return;
        };
        let active_tls_keys: BTreeSet<_> = params
            .participants()
            .participants()
            .iter()
            .map(|(_, _, info)| info.tls_public_key.clone())
            .collect();
        self.foreign_chains
            .get_mut()
            .update_available_chains_config_cache(&active_tls_keys, threshold);
```

**File:** crates/contract/src/primitives/domain.rs (L57-70)
```rust
    if domain.protocol == Protocol::DamgardEtAl {
        let required = t
            .checked_mul(2)
            .and_then(|x| x.checked_sub(1))
            .ok_or(DomainError::ReconstructionThresholdOverflow { threshold: t })?;
        if required > num_participants {
            return Err(DomainError::InsufficientParticipantsForProtocol {
                protocol: domain.protocol,
                required,
                participants: num_participants,
            }
            .into());
        }
    }
```

**File:** crates/contract/src/foreign_chains_metadata.rs (L41-66)
```rust
    pub(crate) fn update_available_chains_config_cache(
        &mut self,
        active_tls_keys: &BTreeSet<dtos::Ed25519PublicKey>,
        threshold: u64,
    ) {
        let mut chain_to_supporter_count: std::collections::BTreeMap<dtos::ForeignChain, u64> =
            std::collections::BTreeMap::new();
        for tls_key in active_tls_keys {
            let Some(chains) = self.foreign_chains_configs.get(tls_key) else {
                continue;
            };
            for chain in chains.iter() {
                if self.rpc_whitelist.entries.is_whitelisted(chain) {
                    let count = chain_to_supporter_count.entry(*chain).or_default();
                    *count = count
                        .checked_add(1)
                        .expect("supporter count bounded by participant set size");
                }
            }
        }
        self.available_foreign_chains = chain_to_supporter_count
            .into_iter()
            .filter_map(|(chain, count)| (count >= threshold).then_some(chain))
            .collect::<BTreeSet<_>>()
            .into();
    }
```

**File:** docs/design/calculating-supported-foreign-chains.md (L106-110)
```markdown
**Liveness** — a request is accepted only when `C` is available (≥ `signing_threshold`
participants cover it), so an accepted request can reach the signing threshold; and a
chain leaves the available set only when more than `n − signing_threshold` nodes drop
it. This strictly improves on the intersection rule, where one non-registering node
dropped a chain to zero availability.
```
