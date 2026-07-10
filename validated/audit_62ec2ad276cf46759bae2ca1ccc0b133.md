### Title
User-Controlled Zero `confirmations` in `BitcoinRpcRequest` Bypasses Finality Check in `verify_foreign_transaction` — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `verify_foreign_transaction` contract method accepts a `BitcoinRpcRequest` whose `confirmations: BlockConfirmations` field is a raw `u64` with no minimum enforced anywhere in the contract or MPC node. An unprivileged caller can set `confirmations = 0`, causing every MPC node to sign a Bitcoin transaction that has zero on-chain finality, enabling double-spend attacks on downstream bridge contracts that trust the MPC threshold signature as proof of settlement.

---

### Finding Description

`verify_foreign_transaction` in `crates/contract/src/lib.rs` accepts a `VerifyForeignTransactionRequestArgs` that embeds a `ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest { confirmations, … })`. [1](#0-0) 

`BlockConfirmations` is defined as a plain `u64` newtype with no minimum-value constraint: [2](#0-1) 

The contract performs no validation on the `confirmations` value before enqueuing the request. The MPC node's `execute_foreign_chain_request` then passes the caller-supplied value verbatim as the `block_confirmations_threshold` to `BitcoinInspector::extract`: [3](#0-2) 

Inside the inspector, the finality gate is:

```rust
let enough_block_confirmations =
    block_confirmations_threshold <= transaction_block_confirmation;
``` [4](#0-3) 

With `confirmations = 0`, the inequality `0 ≤ N` is trivially true for any `N`, including a transaction with zero confirmations (still in the mempool). All MPC nodes independently reach the same conclusion and proceed to produce a threshold signature over the unconfirmed transaction.

This is the direct analog of the zero-slippage vulnerability in the reference report: just as `_amountVoltMin = 0` removes the swap's output floor, `confirmations = 0` removes the bridge's finality floor. Both are user-controlled parameters that can be set to zero with no on-chain guard.

---

### Impact Explanation

The MPC threshold signature is the trust anchor for downstream bridge contracts. A signature produced over a `ForeignTxSignPayload` that embeds `confirmations = 0` attests — falsely — that the Bitcoin transaction is final. An attacker can:

1. Broadcast a Bitcoin transaction to the mempool (0 confirmations).
2. Call `verify_foreign_transaction` with `confirmations = 0` (costs 1 yoctoNEAR).
3. Receive a valid MPC threshold signature over the unconfirmed transaction.
4. Submit that signature to a bridge contract to claim funds on another chain.
5. Replace the original Bitcoin transaction via RBF, or wait for a reorg, effectively double-spending.

This is a **forged foreign-chain verification** that causes **invalid bridge execution and double-spend conditions**, matching the High impact tier.

---

### Likelihood Explanation

Any unprivileged NEAR account can call `verify_foreign_transaction` with `confirmations = 0`. The only barrier is a 1 yoctoNEAR deposit and sufficient prepaid gas. No collusion, privileged role, or special access is required. The attack is fully reachable from an external, unprivileged caller. [5](#0-4) 

---

### Recommendation

Enforce a minimum `confirmations` value at the contract level before enqueuing the request. A governance-controlled `min_bitcoin_confirmations` parameter (e.g., 6) should be stored in `Config` and checked in `verify_foreign_transaction`:

```rust
if let ForeignChainRpcRequest::Bitcoin(ref btc) = request.request {
    if btc.confirmations.0 < self.config.min_bitcoin_confirmations {
        env::panic_str("confirmations below minimum");
    }
}
```

This mirrors the recommendation in the reference report: the owner should enforce a non-zero floor on the safety parameter rather than leaving it entirely to the caller. [6](#0-5) 

---

### Proof of Concept

```json
// Attacker submits to verify_foreign_transaction:
{
  "request": {
    "domain_id": <foreign_tx_domain_id>,
    "payload_version": "V1",
    "request": {
      "Bitcoin": {
        "tx_id": "<mempool_tx_id_not_yet_confirmed>",
        "confirmations": 0,
        "extractors": ["BlockHash"]
      }
    }
  }
}
```

Each MPC node executes:
```
block_confirmations_threshold = 0
enough_block_confirmations = (0 <= actual_confirmations)  // always true
→ inspector proceeds, extracts block hash, signs payload
```

All `t+1` nodes sign. The attacker receives a valid threshold signature over the unconfirmed transaction, submits it to the bridge to claim funds, then RBF-replaces the Bitcoin transaction. [7](#0-6) [8](#0-7)

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1282-1282)
```rust
pub struct BlockConfirmations(pub u64);
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L131-150)
```rust
            dtos::ForeignChainRpcRequest::Bitcoin(request) => {
                let inspector = self
                    .inspectors
                    .bitcoin
                    .as_ref()
                    .context("no inspector configured for bitcoin")?;
                let transaction_id = request.tx_id.0.into();
                let block_confirmations = request.confirmations.0.into();
                let extractors: Vec<BitcoinExtractor> = request
                    .extractors
                    .iter()
                    .cloned()
                    .map(TryInto::try_into)
                    .collect::<Result<_, _>>()?;
                let extracted_values = inspector
                    .extract(transaction_id, block_confirmations, extractors)
                    .timeout(FOREIGN_CHAIN_INSPECTION_TIMEOUT)
                    .await
                    .context("timed out during execution of foreign chain request")??;
                extracted_values.into_iter().map(Into::into).collect()
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

**File:** crates/contract/src/config.rs (L1-1)
```rust
use near_sdk::near;
```
