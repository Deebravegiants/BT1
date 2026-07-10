### Title
Missing Minimum Confirmation Check in `verify_foreign_transaction` Allows Signing Unconfirmed Foreign-Chain Transactions — (File: `crates/foreign-chain-inspector/src/bitcoin/inspector.rs`)

---

### Summary

The `verify_foreign_transaction` contract endpoint accepts a `BitcoinRpcRequest` with `confirmations: 0` (a `BlockConfirmations(u64)` with no minimum enforced). The MPC node's `BitcoinInspector` then checks `block_confirmations_threshold <= transaction_block_confirmation`, which trivially passes when the threshold is 0. This allows any unprivileged caller to obtain a valid MPC threshold signature over an unconfirmed (mempool-only) Bitcoin transaction, enabling double-spend conditions on any bridge that relies on this verification.

---

### Finding Description

`BlockConfirmations` is a plain `u64` newtype with no minimum constraint: [1](#0-0) 

The ABI schema confirms `"minimum": 0.0` is the only bound: [2](#0-1) 

The contract's `verify_foreign_transaction` method passes the caller-supplied `confirmations` value directly into the pending request queue without any validation: [3](#0-2) 

The MPC node's `BitcoinInspector::extract` then evaluates:

```rust
let enough_block_confirmations =
    block_confirmations_threshold <= transaction_block_confirmation;
``` [4](#0-3) 

When `block_confirmations_threshold = BlockConfirmations(0)`, the comparison `0 <= actual_confirmations` is always `true` for any `u64`, including 0 (mempool transaction). The nodes proceed to sign the payload and submit `respond_verify_foreign_tx` to the contract.

---

### Impact Explanation

An attacker can obtain a valid threshold MPC signature over a Bitcoin transaction that has zero block confirmations — i.e., a transaction that is only in the mempool and has not been included in any block. Any bridge contract that uses `verify_foreign_transaction` to gate fund releases on NEAR (or another chain) would release funds based on an unconfirmed transaction. The attacker can then double-spend the Bitcoin transaction (e.g., via RBF or by simply not broadcasting it widely), resulting in a direct loss of funds from the bridge.

**Impact category:** High — forged foreign-chain verification / light-client-style verification bypass causing double-spend conditions.

---

### Likelihood Explanation

- The `verify_foreign_transaction` endpoint is publicly callable by any NEAR account with 1 yoctoNEAR deposit.
- No privileged role or threshold collusion is required.
- The attacker only needs to broadcast a Bitcoin transaction to the mempool (or know a valid mempool tx_id) and submit the request with `confirmations: 0`.
- The Bitcoin RPC `getrawtransaction` returns mempool transactions with `confirmations: 0`, so the node's RPC call succeeds.

---

### Recommendation

Add a minimum confirmation check in the contract's `verify_foreign_transaction` handler (or in `args_into_verify_foreign_tx_request`) before the request is enqueued:

```rust
if let ForeignChainRpcRequest::Bitcoin(ref btc) = request.request {
    require!(
        btc.confirmations.0 >= MIN_BITCOIN_CONFIRMATIONS,
        "Bitcoin confirmations must be at least MIN_BITCOIN_CONFIRMATIONS"
    );
}
```

Alternatively, enforce a per-chain minimum confirmation floor in the `ForeignChainsMetadata` configuration that participants vote on, so the minimum is governance-controlled and chain-specific.

---

### Proof of Concept

1. Attacker broadcasts a Bitcoin transaction `tx_id = T` to the mempool (or identifies an existing mempool tx).
2. Attacker calls `verify_foreign_transaction` on the MPC contract with:
   ```json
   {
     "request": {
       "domain_id": 0,
       "payload_version": "V1",
       "request": {
         "Bitcoin": {
           "tx_id": "<T>",
           "confirmations": 0,
           "extractors": ["BlockHash"]
         }
       }
     }
   }
   ```
   with 1 yoctoNEAR attached.
3. The contract enqueues the request. MPC nodes pick it up and call `getrawtransaction` on their Bitcoin RPC endpoint. The mempool transaction is returned with `confirmations: 0`.
4. The inspector evaluates `0 <= 0` → `true`. Nodes proceed to sign the payload.
5. The contract resolves the yield with a valid `VerifyForeignTransactionResponse` containing a threshold signature.
6. Attacker uses this signature to claim bridge funds on NEAR.
7. Attacker double-spends transaction `T` on Bitcoin (e.g., via RBF), leaving the bridge with a loss.

**Root cause file:** `crates/foreign-chain-inspector/src/bitcoin/inspector.rs`, line 52. [4](#0-3) 

**Entry point:** `crates/contract/src/lib.rs`, `verify_foreign_transaction`. [5](#0-4)

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1282-1282)
```rust
pub struct BlockConfirmations(pub u64);
```

**File:** crates/contract/tests/snapshots/abi__abi_has_not_changed.snap (L2516-2520)
```text
        "BlockConfirmations": {
          "type": "integer",
          "format": "uint64",
          "minimum": 0.0
        },
```

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

**File:** crates/foreign-chain-inspector/src/bitcoin/inspector.rs (L50-59)
```rust
        let transaction_block_confirmation = rpc_response.confirmations.into();
        let enough_block_confirmations =
            block_confirmations_threshold <= transaction_block_confirmation;

        if !enough_block_confirmations {
            return Err(ForeignChainInspectionError::NotEnoughBlockConfirmations {
                expected: block_confirmations_threshold,
                got: transaction_block_confirmation,
            });
        }
```
