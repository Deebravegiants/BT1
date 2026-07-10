### Title
`init_running` Does Not Copy `node_foreign_chain_support` or `foreign_chains` State to the New Contract, Halting Foreign Chain Verification After a Network Transfer - (File: crates/contract/src/lib.rs)

---

### Summary

The `init_running` function, explicitly documented as the mechanism to "transfer the MPC network to a new contract," initializes `node_foreign_chain_support` and `foreign_chains` with empty defaults instead of carrying over the state from the old contract. After a network transfer, `get_available_foreign_chains()` returns an empty set, causing all `verify_foreign_transaction` requests to be silently dropped by nodes until every participant manually re-registers their foreign chain support on the new contract.

---

### Finding Description

`init_running` is the NEAR MPC analog of ZetaChain's `UpdateSystemContract`. Both functions are the designated path for transferring a live protocol instance to a new contract, and both accept the critical cryptographic state (domains, keyset, participants) as explicit arguments. However, just as `UpdateSystemContract` forgot to call `setGasPrice`, `init_running` silently drops two categories of operational state:

**1. `node_foreign_chain_support` (line 2044)**

```rust
node_foreign_chain_support: Default::default(),
```

This `SupportedForeignChainsByNode` map records, for each participant node, which foreign chains it has declared support for. It is the sole input to `get_available_foreign_chains()`, which computes the set of chains for which at least a reconstruction-threshold of nodes have registered support. After `init_running`, this map is empty, so `get_available_foreign_chains()` returns `{}` regardless of what was registered on the old contract.

**2. `foreign_chains` (lines 2045–2048)**

```rust
foreign_chains: Lazy::new(
    StorageKey::ForeignChainMetadata,
    ForeignChainsMetadata::default(),
),
```

This `Lazy<ForeignChainsMetadata>` holds the governance-voted RPC provider whitelist (`rpc_whitelist`) and the per-node foreign chain RPC configurations (`foreign_chains_configs`). Both are reset to empty. Without the whitelist, `register_foreign_chains_config` calls from nodes will fail validation, blocking the re-registration path that would otherwise restore availability.

Compare with the fields that *are* correctly transferred: `domains`, `keyset`, and `parameters` are all passed as explicit arguments and faithfully installed. The omission of the foreign-chain state is structurally identical to the ZetaChain bug: some state is copied, one category is silently dropped. [1](#0-0) [2](#0-1) 

---

### Impact Explanation

After `init_running` completes on the new contract:

- `get_available_foreign_chains()` returns an empty set.
- Nodes consult this view before deciding whether to process a `verify_foreign_transaction` request. With an empty result, no node will pick up the request.
- Every in-flight and new `verify_foreign_transaction` call will time out at the yield-resume boundary, returning an error to the caller.
- The `foreign_chains` RPC whitelist being empty additionally blocks `register_foreign_chains_config`, the primary re-registration path, until participants re-vote the whitelist via `vote_update_foreign_chain_providers`.

This matches the "Medium" allowed impact: **request-lifecycle and contract execution-flow manipulation that breaks a production safety invariant** (foreign chain verification availability) without requiring network-level DoS. The invariant broken is that a network transfer should preserve all operational state, not just cryptographic state. [3](#0-2) 

---

### Likelihood Explanation

`init_running` is the only documented path for transferring the MPC network to a new contract account. It is a planned, governance-approved operation (threshold vote required), not an attacker-injected call. The vulnerability is in the *implementation* of the transfer, not in its access control — exactly as in the ZetaChain report where Admin Group 2 legitimately called `UpdateSystemContract` and the bug manifested. Any future network transfer will trigger this state loss automatically, with no additional attacker action required.

---

### Recommendation

`init_running` should accept the foreign-chain state as additional arguments (mirroring how `domains` and `keyset` are passed), or the caller should be required to supply a snapshot of `node_foreign_chain_support` and `foreign_chains` from the old contract:

```rust
pub fn init_running(
    domains: Vec<DomainConfig>,
    next_domain_id: u64,
    keyset: Keyset,
    parameters: dtos::ThresholdParameters,
    init_config: Option<dtos::InitConfig>,
    // NEW: carry over foreign-chain state
    node_foreign_chain_support: SupportedForeignChainsByNode,
    foreign_chains_metadata: ForeignChainsMetadata,
) -> Result<Self, Error> { ... }
```

Alternatively, the old contract should emit the full state snapshot as a structured argument that the new contract's `init_running` validates and installs atomically.

---

### Proof of Concept

1. Old contract has `node_foreign_chain_support` populated: nodes A, B, C have each called `register_foreign_chain_support` for Bitcoin and Ethereum. `get_available_foreign_chains()` returns `{Bitcoin, Ethereum}`.
2. Participants reach threshold and vote to transfer the network to a new contract account. `init_running` is called on the new contract with the correct `domains`, `keyset`, and `parameters`.
3. New contract initializes `node_foreign_chain_support: Default::default()` — the map is empty.
4. A user calls `verify_foreign_transaction` for a Bitcoin transaction on the new contract. The request is queued.
5. Every node calls `get_available_foreign_chains()` on the new contract before deciding to process the request. The result is `{}`. No node processes the request.

### Citations

**File:** crates/contract/src/lib.rs (L1975-1976)
```rust
    // This function can be used to transfer the MPC network to a new contract.
    #[private]
```

**File:** crates/contract/src/lib.rs (L2039-2051)
```rust
            proposed_updates: Default::default(),
            tee_state,
            accept_requests: true,
            node_migrations: NodeMigrations::default(),
            metrics: Default::default(),
            node_foreign_chain_support: Default::default(),
            foreign_chains: Lazy::new(
                StorageKey::ForeignChainMetadata,
                ForeignChainsMetadata::default(),
            ),
            tee_verifier_account_id: None,
            tee_verifier_votes: TeeVerifierVotes::default(),
        })
```
