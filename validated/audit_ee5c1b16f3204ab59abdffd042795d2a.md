Looking at the external report's vulnerability class — **missing validation of a caller-supplied parameter** (`min_amount_out`) and **missing enforcement of a prerequisite state update** — I need to find an analog in the NEAR MPC codebase where an unprivileged caller can supply an unvalidated parameter that bypasses a safety invariant in the foreign-chain verification flow.

Let me examine the `verify_foreign_transaction` entry point and the Bitcoin inspector's confirmation check.

### Title
Caller-Supplied `confirmations: 0` in `verify_foreign_transaction` Bypasses Bitcoin Finality Requirement, Enabling Signature Over Unconfirmed Transactions — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `verify_foreign_transaction` contract method accepts a `BitcoinRpcRequest` whose `confirmations` field is entirely caller-controlled and is never validated against a protocol-defined minimum. Because the node-side `BitcoinInspector::extract` enforces only `block_confirmations_threshold <= actual_confirmations`, passing `confirmations: 0` makes that check trivially true for any transaction, including mempool-only ones. The MPC network then produces a valid threshold signature over a payload that encodes `confirmations: 0`, permanently weakening the finality guarantee the bridge is supposed to provide.

---

### Finding Description

**Contract entry point — no lower-bound check on `confirmations`:**

In `verify_foreign_transaction` (lines 519–557 of `crates/contract/src/lib.rs`), the contract validates:
- domain exists and has `ForeignTx` purpose
- sufficient gas and deposit
- chain is in the supported-chain whitelist

It does **not** validate any field inside the `ForeignChainRpcRequest` payload, including `BitcoinRpcRequest::confirmations`. [1](#0-0) 

**Node-side inspector — threshold check is trivially satisfied when threshold is 0:**

`BitcoinInspector::extract` enforces:

```rust
let enough_block_confirmations =
    block_confirmations_threshold <= transaction_block_confirmation;
if !enough_block_confirmations {
    return Err(ForeignChainInspectionError::NotEnoughBlockConfirmations { ... });
}
``` [2](#0-1) 

When the caller supplies `confirmations: 0`, `block_confirmations_threshold = 0`, and `0 <= any_u64` is always `true`. Every node in the MPC network independently executes this check and independently passes it, so the threshold-signing protocol proceeds normally.

**Signed payload encodes the caller-supplied `confirmations` value:**

`ForeignTxSignPayloadV1` Borsh-serialises the full `ForeignChainRpcRequest` (including `confirmations`) before hashing:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,   // ← includes confirmations: 0
    pub values: Vec<ExtractedValue>,
}
impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
}
``` [3](#0-2) 

The resulting `payload_hash` — and the threshold ECDSA signature over it — permanently attest that the MPC network verified this transaction with a finality requirement of **zero confirmations**.

---

### Impact Explanation

A malicious user submits `verify_foreign_transaction` with `confirmations: 0` for a Bitcoin transaction that has zero on-chain confirmations (i.e., it is still in the mempool or has just been broadcast). Every honest MPC node independently queries the Bitcoin RPC, finds `0 <= actual_confirmations` true, extracts the requested values, and participates in the threshold signing. The contract then delivers a `VerifyForeignTransactionResponse { payload_hash, signature }` to the caller where `payload_hash` encodes `confirmations: 0`.

Any bridge contract that does not re-derive and compare `payload_hash` against its own expected confirmation threshold will accept this response as proof of a finalised transaction. The attacker can then:

1. Broadcast a Bitcoin transaction spending output O.
2. Immediately call `verify_foreign_transaction(confirmations: 0, tx_id)`.
3. Receive a valid MPC signature before the transaction has a single confirmation.
4. Claim the corresponding NEAR-side asset.
5. Double-spend output O on Bitcoin (e.g., via RBF or a reorg).

This satisfies the **High** impact criterion: *"forged foreign-chain verification … that causes invalid bridge execution or double-spend conditions."* [4](#0-3) 

---

### Likelihood Explanation

The attack requires

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1509)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}

impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```
