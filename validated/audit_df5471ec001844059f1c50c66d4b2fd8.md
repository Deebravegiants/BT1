### Title
Single Byzantine Participant Can Permanently Block All Foreign Chain Verification via `get_supported_foreign_chains()` Strict Intersection Rule — (File: `crates/contract/src/lib.rs`)

---

### Summary

`verify_foreign_transaction` gates on `get_supported_foreign_chains()`, which requires **every** active participant to have registered support for a chain. A single Byzantine participant (strictly below the signing threshold) can call `register_foreign_chain_config` with an empty list to immediately collapse the supported-chain set to empty, permanently blocking all bridge inflow verification requests and locking user funds on the foreign chain.

---

### Finding Description

`verify_foreign_transaction` at `crates/contract/src/lib.rs:533-542` reads the supported chain set at submission time:

```rust
let requested_chain = request.request.chain();
let supported_chains = self.get_supported_foreign_chains();
if !supported_chains.contains(&requested_chain) {
    env::panic_str(...)
}
``` [1](#0-0) 

`get_supported_foreign_chains()` at lines 2176–2217 computes the result as the **strict intersection** of every active participant's registered chains:

```rust
let all_active_nodes_supports_chain =
    nodes_supporting_chain.is_superset(&active_participant_account_ids);
if all_active_nodes_supports_chain {
    Some(foreign_chain)
} else {
    None
}
``` [2](#0-1) 

`register_foreign_chain_config` is callable by any single authenticated participant (enforced via `voter_or_panic()`, not a threshold vote): [3](#0-2) 

Because the intersection requires **all** active participants to support a chain, a single participant registering an empty `ForeignChainConfiguration` causes `get_supported_foreign_chains()` to return an empty set. The design document explicitly acknowledges this root cause:

> "A single node that registers an empty list (or hasn't registered yet) drops every chain — one operator can take the whole feature down." [4](#0-3) 

The analog to TRST-H-2 is direct: just as a malicious actor front-runs pool initialization to set a manipulated interest rate before a liquidity provider's second transaction, a malicious participant can front-run a user's `verify_foreign_transaction` call by submitting `register_foreign_chain_config({})` in the same or preceding block, causing the user's bridge verification to fail at the supported-chain gate.

The threshold-based replacement (`get_available_foreign_chains()`) is already designed and tracked under issue #3434 but **has not yet been deployed** — the production `verify_foreign_transaction` still calls `get_supported_foreign_chains()`: [5](#0-4) 

---

### Impact Explanation

**Medium — contract execution-flow manipulation that breaks production safety/accounting invariants.**

All `verify_foreign_transaction` calls fail with `ForeignChainNotSupported` for every chain. This breaks the primary bridge inflow flow (foreign chain → NEAR via Chain Signatures). Users who have already deposited assets on the foreign chain cannot complete the bridge, effectively locking their funds until the malicious participant re-registers or is removed via a resharing. The invariant violated is that the foreign-chain verification feature should remain available as long as a signing-threshold number of participants support it — a single sub-threshold participant should not be able to take it down.

---

### Likelihood Explanation

**Medium.** The attack requires only a single legitimate participant (strictly below the signing threshold). The participant has concrete economic incentives: blocking a competitor's bridge inflow, extorting users who have already committed funds on the foreign chain, or manipulating token prices by selectively blocking bridge transactions. The on-chain action (`register_foreign_chain_config`) is cheap and takes effect immediately in the same block, enabling reliable front-running of observed pending `verify_foreign_transaction` transactions.

---

### Recommendation

Replace the strict intersection rule in `verify_foreign_transaction` with the threshold-based `get_available_foreign_chains()` already designed in `docs/design/calculating-supported-foreign-chains.md`. Specifically:

1. In `verify_foreign_transaction`, replace `self.get_supported_foreign_chains()` with `self.get_available_foreign_chains()`.
2. `get_available_foreign_chains()` counts, per chain, how many active participants cover it and requires that count to meet the signing threshold — a single non-registering participant cannot drop a chain. [6](#0-5) [7](#0-6) 

---

### Proof of Concept

```
Network: n=4 participants, signing threshold t=3.
Attacker: participant P_1 (single participant, below threshold).

1. User broadcasts verify_foreign_transaction(Bitcoin, tx_id=0xAA...) to NEAR mempool.

2. Attacker observes the pending transaction and front-runs it:
   P_1 calls register_foreign_chain_config({})   // empty ForeignChainConfiguration

3. Contract state after step 2:
   node_foreign_chain_support[P_1] = {}          // P_1 supports no chains

4. get_supported_foreign_chains() evaluates:
   For Bitcoin: nodes_supporting_chain = {P_2, P_3, P_4}
   active_participant_account_ids = {P_1, P_2, P_3, P_4}
   is_superset check: {P_2,P_3,P_4}.is_superset({P_1,P_2,P_3,P_4}) == false
   → Bitcoin is NOT in the supported set.

5. User's verify_foreign_transaction panics:
   InvalidParameters::ForeignChainNotSupported { requested: Bitcoin }

6. User's deposit on the Bitcoin chain is locked.
   Attacker can repeat step 2 indefinitely to block all future requests.
``` [1](#0-0) [2](#0-1)

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

**File:** crates/contract/src/lib.rs (L6992-7014)
```rust
    #[test]
    #[should_panic(expected = "not a voter")]
    fn register_foreign_chain_config__should_reject_non_participant() {
        // Given
        let running_state = gen_running_state(1);
        let mut contract =
            MpcContract::new_from_protocol_state(ProtocolContractState::Running(running_state));
        let foreign_chain_configuration: dtos::ForeignChainConfiguration = BTreeMap::from([(
            dtos::ForeignChain::Bitcoin,
            NonEmptyBTreeSet::new(dtos::RpcProvider {
                rpc_url: "https://btc.example.com".to_string(),
            }),
        )])
        .into();

        let non_participant = gen_account_id();
        let _env = Environment::new(None, Some(non_participant), None);

        // When / Then: a non-participant is rejected. Registration now authenticates via
        // `voter_or_panic()`, which panics rather than returning an error.
        contract
            .register_foreign_chain_config(foreign_chain_configuration)
            .expect("non-participant should not be able to register");
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

**File:** docs/design/calculating-supported-foreign-chains.md (L36-37)
```markdown
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
