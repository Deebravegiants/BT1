### Title
`verify_foreign_transaction` gates on all-participant coverage instead of signing-threshold coverage, allowing a single Byzantine participant to permanently freeze foreign-chain verification - (File: `crates/contract/src/lib.rs`)

---

### Summary

`verify_foreign_transaction` calls `get_supported_foreign_chains()`, which requires **every** participant to have registered support for a chain. The signing threshold is strictly less than the full participant count. A single Byzantine participant below the threshold can therefore block all foreign-chain verification requests by simply not registering support for any chain, even though the MPC network has enough honest participants to sign.

---

### Finding Description

The vulnerability class from the reference report is: an incorrect adjustment factor is applied to a limit before comparing against an actual value, causing the operation to revert when the actual value exceeds the adjusted (but not the true) limit.

The analog here is structural: the "limit" for whether a chain may be requested is the minimum number of participants that must cover it. The **correct** limit is the signing threshold (`t`). The **incorrectly applied** limit is `n` (all participants). When actual coverage satisfies `t ≤ coverage < n`, the request is rejected even though the MPC network can serve it.

**Root cause — `verify_foreign_transaction` in `crates/contract/src/lib.rs`:**

```rust
let supported_chains = self.get_supported_foreign_chains();
if !supported_chains.contains(&requested_chain) {
    env::panic_str(
        &InvalidParameters::ForeignChainNotSupported { requested: requested_chain }
            .to_string(),
    );
}
``` [1](#0-0) 

`get_supported_foreign_chains()` is documented and tested to return only chains supported by **all** participants: [2](#0-1) 

The contract already implements `get_available_foreign_chains()`, which correctly uses the signing threshold: [3](#0-2) 

The design documentation explicitly states the correct invariant:

> "Available chain — a whitelisted chain that at least `signing_threshold` active participants currently cover, so the network can serve it now. `verify_foreign_transaction(C)` is rejected unless `C` is available." [4](#0-3) 

The implementation contradicts this: it uses the all-participant function instead of the threshold-based one.

---

### Impact Explanation

A single Byzantine participant (strictly below the signing threshold) can permanently freeze the entire `verify_foreign_transaction` feature by not registering support for any foreign chain. `get_supported_foreign_chains()` returns the intersection across all participants, so one absent registration empties the set. Every subsequent `verify_foreign_transaction` call panics with `ForeignChainNotSupported`, regardless of how many honest participants cover the chain. This breaks the bridge inbound flow and any contract that depends on foreign-chain attestation.

This matches the allowed Medium impact: *"contract execution-flow manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration."*

---

### Likelihood Explanation

The attack requires only one participant to withhold its `register_foreign_chain_config` / `register_foreign_chains_config` call (or to call it with an empty set). No threshold collusion is needed. The participant does not need to break TEE attestation or leak key material. The entry path is the normal participant registration flow, callable by any attested node.

---

### Recommendation

Replace `get_supported_foreign_chains()` with `get_available_foreign_chains()` in `verify_foreign_transaction`:

```rust
// Before (incorrect — requires all participants):
let supported_chains = self.get_supported_foreign_chains();

// After (correct — requires signing-threshold participants):
let supported_chains = self.get_available_foreign_chains();
``` [1](#0-0) 

---

### Proof of Concept

1. Deploy with 5 participants, signing threshold `t = 3`.
2. Participants 1–4 call `register_foreign_chain_config` with `{Bitcoin}`.
3. Participant 5 (Byzantine) never registers, or registers with an empty set.
4. `get_supported_foreign_chains()` returns `{}` (intersection is empty because participant 5 has no entry).
5. Any call to `verify_foreign_transaction` with `Bitcoin` panics: `"Requested foreign chain, Bitcoin, is not supported."`.
6. The bridge is frozen. Participants 1–4 (honest, above threshold) cannot unblock it without participant 5's cooperation.
7. `get_available_foreign_chains()` would correctly return `{Bitcoin}` (4 ≥ 3), but it is never consulted. [5](#0-4) [3](#0-2)

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

**File:** crates/contract/src/lib.rs (L7017-7059)
```rust
    #[test]
    fn get_supported_foreign_chains__should_return_chains_supported_by_all_participants() {
        // Given
        let running_state = gen_running_state(1);
        let participants = running_state
            .parameters
            .participants()
            .participants()
            .clone();
        let mut contract =
            MpcContract::new_from_protocol_state(ProtocolContractState::Running(running_state));

        // Both participants support Bitcoin and Ethereum
        let foreign_chain_configuration: dtos::ForeignChainConfiguration = BTreeMap::from([
            (
                dtos::ForeignChain::Bitcoin,
                NonEmptyBTreeSet::new(dtos::RpcProvider {
                    rpc_url: "https://btc.example.com".to_string(),
                }),
            ),
            (
                dtos::ForeignChain::Ethereum,
                NonEmptyBTreeSet::new(dtos::RpcProvider {
                    rpc_url: "https://eth.example.com".to_string(),
                }),
            ),
        ])
        .into();

        for (account_id, _, _) in &participants {
            let _env = Environment::new(None, Some(account_id.clone()), None);
            contract
                .register_foreign_chain_config(foreign_chain_configuration.clone())
                .expect("register should succeed");
        }

        // When
        let result = contract.get_supported_foreign_chains();

        // Then
        assert!(result.contains(&dtos::ForeignChain::Bitcoin));
        assert!(result.contains(&dtos::ForeignChain::Ethereum));
        assert_eq!(result.len(), 2);
```

**File:** crates/contract/src/lib.rs (L7602-7647)
```rust
    #[test]
    fn get_available_foreign_chains__should_only_include_whitelisted_chains_with_threshold_coverage()
     {
        // Given: 4 participants, threshold 3. Bitcoin and Ethereum are whitelisted; Solana is not.
        let (_context, mut contract, _) =
            basic_setup_with_protocol(Protocol::CaitSith, DomainPurpose::ForeignTx, &mut OsRng);
        let participants = participant_account_ids(&contract);
        whitelist_chain(&mut contract, dtos::ForeignChain::Bitcoin);
        whitelist_chain(&mut contract, dtos::ForeignChain::Ethereum);

        // When (each participant registers its full covered set in one call, since a
        // registration replaces the participant's previously reported set):
        // - Bitcoin: covered by 3 participants (whitelisted + threshold) -> available.
        // - Ethereum: covered by 1 participant (whitelisted but under threshold) -> not available.
        // - Solana: covered by all 4 (threshold met but not whitelisted) -> not available.
        register_foreign_chain_config(
            &mut contract,
            &participants[0],
            [
                dtos::ForeignChain::Bitcoin,
                dtos::ForeignChain::Ethereum,
                dtos::ForeignChain::Solana,
            ],
        );
        register_foreign_chain_config(
            &mut contract,
            &participants[1],
            [dtos::ForeignChain::Bitcoin, dtos::ForeignChain::Solana],
        );
        register_foreign_chain_config(
            &mut contract,
            &participants[2],
            [dtos::ForeignChain::Bitcoin, dtos::ForeignChain::Solana],
        );
        register_foreign_chain_config(
            &mut contract,
            &participants[3],
            [dtos::ForeignChain::Solana],
        );

        // Then: only Bitcoin is available.
        let available = contract.get_available_foreign_chains();
        assert!(available.contains(&dtos::ForeignChain::Bitcoin));
        assert!(!available.contains(&dtos::ForeignChain::Ethereum));
        assert!(!available.contains(&dtos::ForeignChain::Solana));
        assert_eq!(available.len(), 1);
```

**File:** docs/foreign-chain-transactions.md (L314-317)
```markdown
- **Available chain** — a whitelisted chain that at least `signing_threshold` active participants
  currently cover, so the network can serve it now. Computed dynamically from per-node reports;
  `available ⊆ whitelisted`. `verify_foreign_transaction(C)` is rejected unless `C` is available.
  Returned by `get_available_foreign_chains()`.
```
