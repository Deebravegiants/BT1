### Title
`verify_foreign_transaction` Accepts Requests for Governance-Removed Foreign Chains Due to Missing Whitelist Check — (`File: crates/contract/src/lib.rs`)

### Summary

`verify_foreign_transaction()` gates on `get_supported_foreign_chains()`, which only checks per-node registrations (`node_foreign_chain_support`). It does not consult the on-chain governance-controlled RPC whitelist (`ForeignChainRpcWhitelist`). A chain voted out of the whitelist by governance remains accepted by the contract as long as participants still have it in their per-node registration, directly mirroring the original report's pattern of "registered but no longer valid."

### Finding Description

The contract maintains two distinct chain-validity concepts:

1. **`node_foreign_chain_support`** — per-node self-reported registrations, keyed by `AccountId`. Any participant can add or update this at any time.
2. **`ForeignChainRpcWhitelist`** — the governance-controlled, threshold-voted set of trusted chains and RPC providers. A chain is added or removed only by a threshold vote via `vote_update_foreign_chain_providers`.

The design intent (documented in `docs/design/calculating-supported-foreign-chains.md`) is explicit:

> `verify_foreign_transaction(C)` is **rejected unless `C` is available** … "available" = whitelisted chain that ≥ signing_threshold active participants currently cover.

The function `get_available_foreign_chains()` correctly enforces this by returning a cached set computed in `update_available_chains_config_cache()`, which filters chains through `self.rpc_whitelist.entries.is_whitelisted(chain)`.

However, the production gating check in `verify_foreign_transaction()` calls `get_supported_foreign_chains()` instead:

```rust
// crates/contract/src/lib.rs ~line 533-542
let requested_chain = request.request.chain();
let supported_chains = self.get_supported_foreign_chains();
if !supported_chains.contains(&requested_chain) {
    env::panic_str(...)
}
```

`get_supported_foreign_chains()` (lines 2176–2218) iterates over `node_foreign_chain_support` and checks only whether all active participants have the chain registered — **it never consults the whitelist**:

```rust
// crates/contract/src/lib.rs ~line 2203-2217
foreign_chain_to_node_mapping
    .into_iter()
    .filter_map(|(foreign_chain, nodes_supporting_chain)| {
        let all_active_nodes_supports_chain =
            nodes_supporting_chain.is_superset(&active_participant_account_ids);
        if all_active_nodes_supports_chain { Some(foreign_chain) } else { None }
    })
    ...
```

The whitelist check lives only in `update_available_chains_config_cache()`:

```rust
// crates/contract/src/foreign_chains_metadata.rs ~line 53
if self.rpc_whitelist.entries.is_whitelisted(chain) {
```

This check is never reached by the `verify_foreign_transaction` code path.

### Impact Explanation

When governance votes to remove a chain from the whitelist (e.g., because its RPC providers are compromised or the chain is deprecated), `verify_foreign_transaction` continues to accept user requests for that chain as long as participants still have it in `node_foreign_chain_support`. During the window between the governance vote and participants updating their local configs:

- Nodes still query the chain's (now-untrusted) RPC providers.
- A compromised provider can return fabricated transaction data.
- The MPC network produces a threshold signature attesting to a transaction that never occurred on the foreign chain.
- This enables forged foreign-chain verification and invalid bridge execution — **High impact** per the allowed scope.

Even after nodes update their local configs, the contract still accepts the request (consuming the user's deposit and queuing a request that will time out), breaking request-lifecycle accounting invariants — **Medium impact** per the allowed scope.

### Likelihood Explanation

- The whitelist feature is implemented and deployed (`ForeignChainRpcWhitelist`, `vote_update_foreign_chain_providers`).
- Any unprivileged user can call `verify_foreign_transaction` with any chain argument.
- The window between a governance removal vote and all nodes updating their local configs is non-zero and operationally realistic.
- No privileged access is required to trigger the vulnerability.

### Recommendation

Replace the gating check in `verify_foreign_transaction()` with `get_available_foreign_chains()` (which enforces the whitelist) instead of `get_supported_foreign_chains()`:

```rust
// Replace:
let supported_chains = self.get_supported_foreign_chains();
// With:
let supported_chains = self.get_available_foreign_chains();
```

Ensure `update_available_chains_config_cache()` is called whenever the whitelist or participant set changes, so the cached `available_foreign_chains` is always current.

### Proof of Concept

1. Governance votes chain `X` into the whitelist; all participants register support for `X` in `node_foreign_chain_support`.
2. Governance votes chain `X` out of the whitelist (e.g., `vote_update_foreign_chain_providers` removes it). `get_available_foreign_chains()` now returns a set excluding `X`.
3. Participants have not yet updated their local configs; `node_foreign_chain_support` still contains `X` for all participants.
4. Attacker calls `verify_foreign_transaction({ chain: X, ... })`.
5. Contract evaluates `get_supported_foreign_chains()` → returns `X` (all participants still registered). **No whitelist check is performed.**
6. Request is accepted and queued. Nodes query the now-untrusted RPC providers for chain `X`.
7. A compromised provider returns fabricated data; nodes produce signature shares; the MPC network issues a threshold signature over a forged foreign-chain observation.

**Root cause file/line**: [1](#0-0) 

**Missing whitelist enforcement**: [2](#0-1) 

**Correct whitelist check (unused by this path)**: [3](#0-2) 

**Design intent confirming the bug**: [4](#0-3)

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

**File:** crates/contract/src/lib.rs (L2176-2218)
```rust
    pub fn get_supported_foreign_chains(&self) -> dtos::SupportedForeignChains {
        let active_participant_account_ids = self
            .protocol_state
            .active_participants()
            .participants()
            .iter()
            .map(|(account_id, _, _)| account_id.clone())
            .collect::<BTreeSet<_>>();

        let mut foreign_chain_to_node_mapping: BTreeMap<
            &dtos::ForeignChain,
            BTreeSet<dtos::AccountId>,
        > = BTreeMap::new();

        for (account_id, chains) in self
            .node_foreign_chain_support
            .foreign_chain_support_by_node
            .iter()
        {
            for chain in chains.iter() {
                foreign_chain_to_node_mapping
                    .entry(chain)
                    .or_default()
                    .insert(account_id.clone());
            }
        }

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

**File:** docs/design/calculating-supported-foreign-chains.md (L29-34)
```markdown
- **Available** is computed dynamically from the per-node config reports: `C` is available iff
  ≥ `signing_threshold` active participants cover `C`. `available ⊆ whitelisted` always.

`verify_foreign_transaction(C)` is **rejected unless `C` is available**: the contract fails fast
instead of accepting a request that can't reach the signing threshold and letting it time out. The
rejection is temporary — `C` becomes serviceable again as soon as enough nodes report coverage.
```
