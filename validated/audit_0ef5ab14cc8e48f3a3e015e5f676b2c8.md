### Title
Single Participant's Missing or Empty Foreign-Chain Registration Freezes All `verify_foreign_transaction` Requests - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `get_supported_foreign_chains()` function enforces a strict **all-or-nothing intersection rule**: a foreign chain is only considered supported if **every single active participant** has registered it. A single Byzantine participant strictly below the signing threshold can freeze the entire `verify_foreign_transaction` feature by registering an empty chain list or simply never registering, causing all bridge requests to be permanently rejected.

---

### Finding Description

`get_supported_foreign_chains()` computes the supported set by iterating over `node_foreign_chain_support` and then filtering to chains where `nodes_supporting_chain.is_superset(&active_participant_account_ids)`:

```rust
// lib.rs:2203-2214
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
``` [1](#0-0) 

This means if **any** active participant has not called `register_foreign_chain_config` yet, or calls it with an empty `ForeignChainConfiguration` map (which is structurally valid — it is a `BTreeMap` with zero entries), that participant is absent from `nodes_supporting_chain` for every chain, causing `is_superset` to return `false` for all chains, and the returned supported set is empty.

`verify_foreign_transaction` then gates on this set and panics for every request:

```rust
// lib.rs:533-542
let supported_chains = self.get_supported_foreign_chains();
if !supported_chains.contains(&requested_chain) {
    env::panic_str(
        &InvalidParameters::ForeignChainNotSupported {
            requested: requested_chain,
        }
        .to_string(),
    );
}
``` [2](#0-1) 

The design documentation explicitly acknowledges this root cause:

> "A single node that registers an empty list (or hasn't registered yet) drops **every** chain — one operator can take the whole feature down." [3](#0-2) 

The sandbox test `register_foreign_chain_config__returns_empty_when_not_all_registered` confirms that if only one participant registers, the supported set is empty even though that participant registered a valid chain: [4](#0-3) 

---

### Impact Explanation

All `verify_foreign_transaction` requests for every foreign chain are rejected with `ForeignChainNotSupported` for as long as any single active participant has not registered or has registered an empty configuration. This permanently freezes the bridge's inbound flow (foreign chain → NEAR) until the non-registering participant acts. The freeze is not limited to one chain — it drops **all** chains simultaneously. This matches the **Medium** allowed impact: *request-lifecycle and contract execution-flow manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration.*

---

### Likelihood Explanation

In a network of `n` participants with signing threshold `t < n`, any **single** participant (strictly below threshold) can trigger this. The attacker's required action is minimal: call `register_foreign_chain_config` with an empty `BTreeMap`, or simply never call it after joining the participant set. No key material, no collusion, and no network-level attack is required. The `register_foreign_chain_config` method is callable by any active participant: [5](#0-4) 

---

### Recommendation

Replace the strict `is_superset` (all-participants) rule with a threshold-based rule: a chain is supported if at least `signing_threshold` active participants have registered it. This is exactly the fix proposed in the design document (tracked as issue #3434):

> "Available is computed dynamically from the per-node config reports: C is available iff ≥ signing_threshold active participants cover C." [6](#0-5) 

The contract already has `signing_threshold` accessible via `self.protocol_state.threshold()`. The filter in `get_supported_foreign_chains()` should be changed from `is_superset(&active_participant_account_ids)` to `nodes_supporting_chain.len() >= signing_threshold`.

---

### Proof of Concept

1. Network has 5 active participants, signing threshold = 3. All 4 participants register `{Bitcoin, Ethereum}`.
2. Participant 5 (a Byzantine node below threshold) calls `register_foreign_chain_config({})` — an empty map.
3. `get_supported_foreign_chains()` builds `nodes_supporting_chain` for Bitcoin = `{P1, P2, P3, P4}`.
4. `is_superset(&{P1,P2,P3,P4,P5})` → `false` (P5 is missing).
5. Same for Ethereum. The returned set is `{}`.
6. Any user calling `verify_foreign_transaction` for Bitcoin or Ethereum receives `ForeignChainNotSupported` and their bridge request is permanently rejected. [7](#0-6)

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

**File:** crates/contract/src/lib.rs (L2176-2183)
```rust
    pub fn get_supported_foreign_chains(&self) -> dtos::SupportedForeignChains {
        let active_participant_account_ids = self
            .protocol_state
            .active_participants()
            .participants()
            .iter()
            .map(|(account_id, _, _)| account_id.clone())
            .collect::<BTreeSet<_>>();
```

**File:** crates/contract/src/lib.rs (L2185-2217)
```rust
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
```

**File:** docs/design/calculating-supported-foreign-chains.md (L9-13)
```markdown
Today, `get_supported_foreign_chains()` returns the **strict intersection** of every
active participant's registered chains, and `verify_foreign_transaction` rejects any
request whose target chain is not in it. A single node that registers an empty list
(or hasn't registered yet) drops **every** chain — one operator can take the whole
feature down. That is what this proposal fixes.
```

**File:** docs/design/calculating-supported-foreign-chains.md (L29-34)
```markdown
- **Available** is computed dynamically from the per-node config reports: `C` is available iff
  ≥ `signing_threshold` active participants cover `C`. `available ⊆ whitelisted` always.

`verify_foreign_transaction(C)` is **rejected unless `C` is available**: the contract fails fast
instead of accepting a request that can't reach the signing threshold and letting it time out. The
rejection is temporary — `C` becomes serviceable again as soon as enough nodes report coverage.
```

**File:** crates/contract/tests/sandbox/foreign_chain_configuration.rs (L204-240)
```rust
#[tokio::test]
async fn register_foreign_chain_config__returns_empty_when_not_all_registered(
    #[case] method_name: &str,
    #[case] bitcoin_only: serde_json::Value,
) {
    // Given: a running contract with participants
    let SandboxTestSetup {
        contract,
        mpc_signer_accounts,
        ..
    } = SandboxTestSetup::builder()
        .with_protocols(ALL_PROTOCOLS)
        .build()
        .await;

    // When: only one participant registers
    let result = mpc_signer_accounts[0]
        .call(contract.id(), method_name)
        .args_json(bitcoin_only.clone())
        .transact()
        .await
        .unwrap()
        .into_result();
    assert_matches!(result, Ok(_));

    // Then: get_supported_foreign_chains returns empty (not all participants registered)
    let supported: Vec<String> = contract
        .view("get_supported_foreign_chains")
        .await
        .unwrap()
        .json()
        .unwrap();
    assert!(
        supported.is_empty(),
        "should be empty when not all participants have registered"
    );
}
```
