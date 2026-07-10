### Title
`vote_pk` Missing `recompute_available_foreign_chains()` After Initializing→Running Transition - (File: crates/contract/src/lib.rs)

### Summary

The `vote_pk` function, which finalizes key generation and transitions the contract from `Initializing` to `Running`, does not call `recompute_available_foreign_chains()`. The parallel transition path `vote_reshared` (Resharing→Running) does call it. This leaves the `available_foreign_chains` cache stale after every key-generation cycle, silently breaking `verify_foreign_transaction` request routing until a participant manually re-registers their foreign-chain config.

### Finding Description

Two contract functions both produce a `Running` state as their terminal output:

**`vote_reshared`** (Resharing → Running): [1](#0-0) 

```rust
if let Some(new_state) = self.protocol_state.vote_reshared(key_event_id)? {
    self.protocol_state = new_state;
    self.recompute_available_foreign_chains();   // ← PRESENT
    ...
```

**`vote_pk`** (Initializing → Running): [2](#0-1) 

```rust
if let Some(new_state) = self.protocol_state.vote_pk(key_event_id, extended_key)? {
    self.protocol_state = new_state;
    // recompute_available_foreign_chains() is ABSENT
}
```

`recompute_available_foreign_chains` rebuilds the `available_foreign_chains` cache by intersecting the current participant TLS-key set with each node's registered foreign-chain config and the RPC whitelist: [3](#0-2) 

During `Initializing` state the function is a deliberate no-op (it returns early because the state is neither `Running` nor `Resharing`): [4](#0-3) 

Nodes are permitted to call `register_foreign_chains_config` while the contract is in `Initializing` state (the participant-check accepts existing participants): [5](#0-4) 

Each such call invokes `recompute_available_foreign_chains()` internally, but because the contract is still `Initializing`, the recompute is silently skipped and the cache is not updated. When `vote_pk` later transitions to `Running`, the cache remains at whatever value it held before the `Initializing` phase began — empty on first boot, or reflecting a potentially outdated participant/config snapshot on subsequent domain additions.

The `available_foreign_chains` cache is the sole gate used to determine which foreign chains are serviceable: [6](#0-5) 

### Impact Explanation

After every successful key-generation cycle (`vote_add_domains` → `vote_pk`), the `available_foreign_chains` cache is stale. On first boot (the most common deployment path), the cache is empty. Any `verify_foreign_transaction` call targeting a legitimately supported chain will be rejected with "chain not available" until at least one participant re-calls `register_foreign_chains_config` to force a recompute. This breaks the foreign-chain verification request lifecycle — a Medium impact per the allowed scope ("request-lifecycle … manipulation that breaks production safety/accounting invariants").

### Likelihood Explanation

This is triggered by the normal, mandatory protocol flow: every new domain addition goes through `vote_add_domains` → `vote_pk`. On a freshly deployed contract the very first key generation leaves the cache empty. No attacker action is required; the bug fires automatically on every key-generation completion.

### Recommendation

Add `self.recompute_available_foreign_chains();` immediately after the state assignment in `vote_pk`, mirroring the pattern in `vote_reshared`:

```rust
if let Some(new_state) = self.protocol_state.vote_pk(key_event_id, extended_key)? {
    self.protocol_state = new_state;
    self.recompute_available_foreign_chains(); // add this
}
```

The same audit should be applied to `vote_cancel_resharing` and `vote_cancel_keygen`, which also produce a `Running` terminal state and may share the same omission.

### Proof of Concept

1. Deploy the contract and call `init` (Running, no domains, cache empty).
2. All participants call `vote_add_domains` with a `ForeignTx` domain → contract enters `Initializing`.
3. All participants call `register_foreign_chains_config` with Bitcoin → storage updated, but `recompute_available_foreign_chains()` is a no-op (Initializing state), cache stays empty.
4. All participants call `vote_pk` with the agreed public key → contract transitions to `Running`. Cache is still empty.
5. Any user calls `verify_foreign_transaction` for Bitcoin → rejected because `available_foreign_chains` is empty, even though threshold-many nodes have registered Bitcoin support.
6. One participant calls `register_foreign_chains_config` again → `recompute_available_foreign_chains()` now runs in Running state → cache is populated → `verify_foreign_transaction` succeeds.

The window between step 4 and step 6 is the broken state, and it persists indefinitely until an operator manually triggers a re-registration.

### Citations

**File:** crates/contract/src/lib.rs (L1008-1022)
```rust
        let is_participant = self
            .protocol_state
            .is_existing_or_prospective_participant(&node_id.account_id)?;
        if !is_participant {
            return Err(InvalidState::NotParticipant {
                account_id: node_id.account_id.clone(),
            }
            .into());
        }
        let tls_key = node_id.tls_public_key.clone();

        self.foreign_chains
            .get_mut()
            .register(tls_key, foreign_chains_config);
        self.recompute_available_foreign_chains();
```

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

**File:** crates/contract/src/lib.rs (L1126-1130)
```rust
        if let Some(new_state) = self.protocol_state.vote_pk(key_event_id, extended_key)? {
            self.protocol_state = new_state;
        }

        Ok(())
```

**File:** crates/contract/src/lib.rs (L1170-1173)
```rust
        if let Some(new_state) = self.protocol_state.vote_reshared(key_event_id)? {
            // Resharing has concluded, transition to running state
            self.protocol_state = new_state;
            self.recompute_available_foreign_chains();
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
