### Title
Inconsistency Between `get_available_foreign_chains()` View and `verify_foreign_transaction()` Execution Gate — (`File: crates/contract/src/lib.rs`)

### Summary

`verify_foreign_transaction()` gates on `get_supported_foreign_chains()` (the legacy all-participant intersection rule), while the documented and user-facing availability view is `get_available_foreign_chains()` (threshold-based). A user or dApp that queries `get_available_foreign_chains()` to determine whether a foreign-chain verification request will be accepted will receive a false positive: the view says the chain is available, but the execution function rejects the transaction.

### Finding Description

Two separate foreign-chain view functions exist in the contract, computing availability using fundamentally different logic and different underlying data structures:

**`get_supported_foreign_chains()`** (lines 2176–2218) reads from `self.node_foreign_chain_support.foreign_chain_support_by_node` and applies a **strict intersection rule**: a chain is returned only if every single active participant has registered it. [1](#0-0) 

**`get_available_foreign_chains()`** (lines 2226–2228) reads from `self.foreign_chains.get().available_foreign_chains`, a cached value populated by `recompute_available_foreign_chains()` using a **threshold-based rule**: a chain is available if ≥ `reconstruction_threshold` active participants cover it. [2](#0-1) 

The threshold-based cache is updated via `register_foreign_chains_config()` → `recompute_available_foreign_chains()`: [3](#0-2) 

However, `verify_foreign_transaction()` — the actual execution function — gates on `get_supported_foreign_chains()`, not `get_available_foreign_chains()`: [4](#0-3) 

The design documentation explicitly states that `verify_foreign_transaction(C)` must be rejected unless `C` is in the **available** set (threshold-based), and that `get_supported_foreign_chains()` (intersection rule) is to be deprecated: [5](#0-4) 

The two registration paths are also separate: `register_foreign_chain_support()` feeds `node_foreign_chain_support` (consumed by `get_supported_foreign_chains()`), while `register_foreign_chains_config()` feeds `foreign_chains` (consumed by `get_available_foreign_chains()`). [6](#0-5) [7](#0-6) 

### Impact Explanation

A user or dApp that calls `get_available_foreign_chains()` — the documented, intended gating view — to check whether a chain is serviceable before submitting `verify_foreign_transaction()` will receive a false positive whenever:

- Nodes have registered via `register_foreign_chains_config()` (new path), making `get_available_foreign_chains()` show the chain as available (threshold met, e.g., 3 of 4 participants)
- But `node_foreign_chain_support` (old path) is not fully populated, so `get_supported_foreign_chains()` returns an empty or smaller set (intersection rule requires all 4)

The result: `verify_foreign_transaction()` panics and rejects the request for a chain that the canonical view function says is available. This breaks the foreign-chain bridge execution flow and causes request-lifecycle invariant violations — accepted by the view, rejected by execution.

This matches the allowed Medium impact: **contract execution-flow manipulation that breaks production safety/accounting invariants**.

### Likelihood Explanation

This is reachable by any unprivileged caller submitting a `verify_foreign_transaction()` request. The inconsistency is structural and permanent until the execution function is updated. It is triggered whenever nodes migrate to the new `register_foreign_chains_config()` registration path (which is the intended migration path per the design doc), making the two data stores diverge. No privileged access or collusion is required.

### Recommendation

Change `verify_foreign_transaction()` to gate on `get_available_foreign_chains()` instead of `get_supported_foreign_chains()`, consistent with the documented design intent:

```rust
// Replace:
let supported_chains = self.get_supported_foreign_chains();
if !supported_chains.contains(&requested_chain) { ... }

// With:
let available_chains = self.get_available_foreign_chains();
if !available_chains.contains(&requested_chain) { ... }
```

This makes the execution function consistent with the view function that users and dApps are expected to query.

### Proof of Concept

1. Deploy the contract with 4 participants, governance threshold 3, ForeignTx domain reconstruction_threshold 3.
2. Whitelist Bitcoin via `vote_update_foreign_chain_providers`.
3. Have 3 of 4 participants call `register_foreign_chains_config([Bitcoin])` (new path). The 4th participant does not register.
4. Call `get_available_foreign_chains()` → returns `[Bitcoin]` (threshold 3 met). ✓
5. Call `get_supported_foreign_chains()` → returns `[]` (intersection rule: 4th participant missing). ✗
6. Submit `verify_foreign_transaction({ chain: Bitcoin, ... })` → **panics with `ForeignChainNotSupported`**, despite step 4 showing Bitcoin as available. [4](#0-3) [8](#0-7)

### Citations

**File:** crates/contract/src/lib.rs (L533-542)
```rust
        let requested_chain = request.request.chain();
        let supported_chains = self.get_supported_foreign_chains();
        if !supported_chains.contains(&requested_chain) {
            env::panic_str(
                &InvalidParameters::ForeignChainNotSupported {
                    requested: requested_chain,
                }
                .to_string(),
            );
        }
```

**File:** crates/contract/src/lib.rs (L971-983)
```rust
    #[handle_result]
    pub fn register_foreign_chain_support(
        &mut self,
        foreign_chain_support: dtos::SupportedForeignChains,
    ) -> Result<(), Error> {
        let account_id = self.voter_or_panic();

        self.node_foreign_chain_support
            .foreign_chain_support_by_node
            .insert(account_id, foreign_chain_support);

        Ok(())
    }
```

**File:** crates/contract/src/lib.rs (L986-1025)
```rust
    #[handle_result]
    pub fn register_foreign_chains_config(
        &mut self,
        foreign_chains_config: dtos::ForeignChainsConfig,
    ) -> Result<(), Error> {
        Self::assert_caller_is_signer();
        let signer_account_id = env::signer_account_id();
        let signer_account_pk = env::signer_account_pk();
        let signer_account_ed25519_pk = Ed25519PublicKey::try_from(&signer_account_pk)
            .unwrap_or_else(|_| env::panic_str("signer account key must be Ed25519"));
        let node_id = self
            .tee_state
            .lookup_node_id_by_signer_pk(&signer_account_ed25519_pk)
            .map_err(|_| InvalidState::NotParticipant {
                account_id: signer_account_id.clone(),
            })?;
        if node_id.account_id != signer_account_id {
            return Err(InvalidState::NotParticipant {
                account_id: signer_account_id,
            }
            .into());
        }
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

        Ok(())
    }
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

**File:** crates/contract/src/lib.rs (L2203-2217)
```rust
        foreign_chain_to_node_mapping
            .into_iter()
            .filter_map(|(foreign_chain, nodes_supporting_chain)| {
                let all_active_nodes_supports_chain =
                    nodes_supporting_chain.is_superset(&active_participant_account_ids);

                if all_active_nodes_supports_chain {
                    Some(foreign_chain)
                } else {
                    None
                }
            })
            .cloned()
            .collect::<BTreeSet<dtos::ForeignChain>>()
            .into()
```

**File:** crates/contract/src/lib.rs (L2226-2228)
```rust
    pub fn get_available_foreign_chains(&self) -> dtos::AvailableForeignChains {
        self.foreign_chains.get().available_foreign_chains.clone()
    }
```

**File:** docs/design/calculating-supported-foreign-chains.md (L32-37)
```markdown
`verify_foreign_transaction(C)` is **rejected unless `C` is available**: the contract fails fast
instead of accepting a request that can't reach the signing threshold and letting it time out. The
rejection is temporary — `C` becomes serviceable again as soon as enough nodes report coverage.

The legacy `get_supported_foreign_chains()` (the intersection rule) is **to be deprecated** in favour
of the two views above.
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
