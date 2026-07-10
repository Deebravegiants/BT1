### Title
Single Byzantine Participant Can Block All `verify_foreign_transaction` Requests via Empty Chain Registration — (`crates/contract/src/lib.rs`)

---

### Summary

The `get_supported_foreign_chains()` function uses a **strict all-participant intersection rule**: a chain is only considered supported if every single active participant has registered it. A single Byzantine participant (strictly below the signing threshold) can register an empty foreign-chain list, causing `get_supported_foreign_chains()` to return an empty set. Because `verify_foreign_transaction` panics immediately when the requested chain is not in that set, **all foreign-chain verification requests are permanently blocked** until the Byzantine participant re-registers a non-empty list.

This is the direct analog of the Napier M-10 bug: upstream state (a participant's empty registration) silently reduces a computed set to zero/empty, and the downstream function (`verify_foreign_transaction`) has no guard for that empty result — it panics unconditionally.

---

### Finding Description

**Step 1 — Attacker registers an empty chain list.**

Any active participant can call `register_foreign_chain_support` (gated only by `voter_or_panic()`, i.e., participant membership) with an empty `BTreeSet`:

```rust
// crates/contract/src/lib.rs ~4387
contract.register_foreign_chain_support(BTreeSet::new().into())
``` [1](#0-0) 

**Step 2 — `get_supported_foreign_chains()` returns an empty set.**

The function computes the strict intersection: for each chain, it checks whether the set of nodes that registered that chain is a **superset of all active participants**. Because the Byzantine participant is in `active_participant_account_ids` but absent from every chain's supporter set, no chain passes the `is_superset` check:

```rust
// crates/contract/src/lib.rs ~2203-2216
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
``` [2](#0-1) 

**Step 3 — `verify_foreign_transaction` panics for every chain.**

The function has no guard for an empty supported-chain set. It unconditionally panics when the requested chain is absent:

```rust
// crates/contract/src/lib.rs ~533-542
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
``` [3](#0-2) 

The codebase's own design document explicitly acknowledges this root cause:

> "A single node that registers an empty list (or hasn't registered yet) drops **every** chain — one operator can take the whole feature down." [4](#0-3) 

The e2e test `supported_foreign_chains__should_require_all_participants_to_register` empirically confirms that one node with an empty registration prevents any chain from appearing in the supported set: [5](#0-4) 

---

### Impact Explanation

Foreign-chain transaction verification (`verify_foreign_transaction`) is a core protocol feature: it is the entry point for cross-chain bridge flows. With the supported-chain set forced to empty, every call to `verify_foreign_transaction` panics with `ForeignChainNotSupported`, regardless of which chain is requested. All pending and future foreign-chain verification requests are blocked for the duration of the attack. This matches the **Medium** allowed impact: *"contract execution-flow manipulation that breaks production safety/accounting invariants."*

---

### Likelihood Explanation

The attack requires only a single active participant — strictly below the signing threshold — to call `register_foreign_chain_support` with an empty argument. This is a normal, permissioned contract call available to every participant. No key compromise, no collusion, and no network-level access is needed. The call is cheap and can be repeated to sustain the DoS.

---

### Recommendation

Replace the strict all-participant intersection with a **threshold-based availability check**, exactly as proposed in `docs/design/calculating-supported-foreign-chains.md`: a chain is available if at least `signing_threshold` active participants cover it. This is already tracked internally and the design is fully specified. [6](#0-5) 

As an immediate short-circuit guard (analogous to the Napier fix), `verify_foreign_transaction` could also return a graceful error instead of panicking when `supported_chains` is empty, preventing a single registration from causing a hard revert.

---

### Proof of Concept

1. Deploy the contract in Running state with participants `[A, B, C]`, threshold 2.
2. All three participants register `{Bitcoin}` → `get_supported_foreign_chains()` returns `{Bitcoin}`.
3. Participant `A` (Byzantine, below threshold) calls `register_foreign_chain_support({})` (empty set).
4. `get_supported_foreign_chains()` now returns `{}` — the `is_superset` check fails for Bitcoin because `A` is in `active_participant_account_ids` but not in Bitcoin's supporter set.
5. Any user calls `verify_foreign_transaction` for Bitcoin → contract panics with `ForeignChainNotSupported`.
6. The attack is sustained as long as `A` keeps its empty registration. No threshold of honest participants can override it under the current intersection rule. [7](#0-6) [8](#0-7)

### Citations

**File:** crates/contract/src/lib.rs (L519-557)
```rust
    pub fn verify_foreign_transaction(&mut self, request: VerifyForeignTransactionRequestArgs) {
        log!(
            "verify_foreign_transaction: predecessor={:?}, request={:?}",
            env::predecessor_account_id(),
            request
        );

        self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::ForeignTx,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );

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

        let callback_gas = Gas::from_tgas(
            self.config
                .return_signature_and_clean_state_on_success_call_tera_gas,
        );

        let request = args_into_verify_foreign_tx_request(request);
        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_VERIFY_FOREIGN_TX_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_verify_foreign_tx_request(request, id),
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

**File:** crates/contract/src/lib.rs (L4387-4392)
```rust
    fn register_foreign_chain_support__should_panic_when_predecessor_differs_from_signer() {
        let mut contract = forwarded_participant_call_contract();
        contract
            .register_foreign_chain_support(BTreeSet::new().into())
            .expect("expected panic when predecessor != signer");
    }
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

**File:** crates/e2e-tests/tests/foreign_chain_configuration.rs (L48-97)
```rust
async fn supported_foreign_chains__should_require_all_participants_to_register() {
    // given — 3-node cluster with foreign chains on nodes 0 and 1 only
    let (cluster, _running) =
        common::must_setup_cluster(common::FOREIGN_CHAIN_POLICY_PORT_SEED, |c| {
            c.node_foreign_chains_configs = vec![
                solana_foreign_chains_config(), // node 0
                solana_foreign_chains_config(), // node 1
                ForeignChainsConfig::default(), // node 2 — no foreign chains
            ];
        })
        .await;

    // when — wait for all three nodes to register (one with an empty configuration)
    // without Solana becoming supported
    (|| async {
        let registrations = cluster
            .view_foreign_chain_configurations()
            .await
            .expect("failed to view configurations");
        let supported = cluster
            .view_foreign_chains_supported_by_contract()
            .await
            .expect("failed to view supported chains");

        let configurations = &registrations.foreign_chain_support_by_node;
        anyhow::ensure!(
            configurations.len() == 3,
            "expected exactly 3 registrations, got {}",
            configurations.len()
        );
        let empty_registrations = configurations.values().filter(|c| c.is_empty()).count();
        anyhow::ensure!(
            empty_registrations == 1,
            "expected exactly 1 empty registration (node 2), got {empty_registrations}"
        );
        anyhow::ensure!(
            !supported.contains(&ForeignChain::Solana),
            "Solana should not be supported before all participants register it"
        );
        Ok(())
    })
    .retry(
        ConstantBuilder::default()
            .with_delay(common::POLL_INTERVAL)
            .with_max_times(
                (CLUSTER_WAIT_TIMEOUT.as_millis() / common::POLL_INTERVAL.as_millis()) as usize,
            ),
    )
    .await
    .expect("timed out waiting for all three registrations with one empty");
```
