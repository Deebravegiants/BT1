### Title
Zero `BlockConfirmations` Accepted in `verify_foreign_transaction`, Enabling Signature Over Unfinalized Bitcoin Transactions - (File: `crates/contract/src/lib.rs`, `crates/foreign-chain-inspector/src/bitcoin/inspector.rs`)

---

### Summary

`verify_foreign_transaction` accepts a caller-supplied `BlockConfirmations` value of `0` for Bitcoin requests without any on-chain or node-side minimum enforcement. Because the Bitcoin inspector's finality gate is `block_confirmations_threshold <= transaction_block_confirmation`, a threshold of `0` is trivially satisfied by any transaction with even a single confirmation (or any non-negative confirmation count). The MPC network will then produce a valid threshold signature attesting to a Bitcoin transaction that has not reached any meaningful finality, enabling a bridge double-spend.

---

### Finding Description

`BlockConfirmations` is a plain `u64` newtype with no enforced lower bound: [1](#0-0) 

The ABI schema explicitly exposes `"minimum": 0.0`: [2](#0-1) 

The contract's `verify_foreign_transaction` entry point performs four precondition checks — domain purpose, gas, deposit, and chain availability — but **never validates the `confirmations` field**: [3](#0-2) 

The Bitcoin inspector enforces finality with a single `<=` comparison: [4](#0-3) 

When `block_confirmations_threshold = 0`, the condition `0 <= transaction_block_confirmation` is always `true` for any mined transaction (confirmation count ≥ 1). The inspector proceeds to `verify_block_is_canonical` and then signs the payload. The signed `ForeignTxSignPayloadV1` commits to the full `ForeignChainRpcRequest` including `confirmations: 0`, so the signature is over a payload that explicitly encodes zero-confirmation finality: [1](#0-0) 

---

### Impact Explanation

The `verify_foreign_transaction` flow exists specifically to let NEAR bridge contracts react to foreign-chain events without a trusted relayer. The MPC signature is the attestation that a foreign transaction finalized. If an attacker can obtain a valid MPC signature over a Bitcoin transaction with `confirmations: 0`, the bridge contract receives a cryptographically valid attestation for a transaction that may be reorganized out of the chain. The attacker can:

1. Broadcast a Bitcoin transaction to the bridge deposit address.
2. Immediately call `verify_foreign_transaction` with `confirmations: 0` before any reorg risk has passed.
3. Receive a valid MPC threshold signature attesting to the transaction.
4. Redeem bridge funds on NEAR using the signature.
5. Attempt to double-spend or reorg the Bitcoin transaction.

This matches the **High** impact class: *forged foreign-chain verification / light-client-style verification bypass that causes invalid bridge execution or double-spend conditions*.

---

### Likelihood Explanation

The attack path requires only an unprivileged NEAR account and a 1-yoctonear deposit. No threshold collusion, no privileged access, and no TEE bypass is needed. The `confirmations` field is fully caller-controlled and the contract imposes no floor. Any bridge integrator or malicious user can trigger this by constructing a `BitcoinRpcRequest` with `confirmations: 0`.

---

### Recommendation

Enforce a protocol-defined minimum confirmation count on-chain inside `verify_foreign_transaction` before the request is enqueued. For Bitcoin, the industry standard is 6 confirmations; at minimum, reject `confirmations: 0`. A configurable per-chain floor stored in the contract's `ForeignChainRpcWhitelist` / `ChainEntry` (alongside `quorum`) would allow governance to tune the value without a code upgrade. The same pattern should be reviewed for any future chain family that uses a numeric finality parameter rather than a finality-level enum.

```rust
// In verify_foreign_transaction, before enqueue_yield_request:
if let ForeignChainRpcRequest::Bitcoin(ref btc) = request.request {
    if btc.confirmations.0 == 0 {
        env::panic_str("Bitcoin confirmations must be > 0");
    }
}
```

---

### Proof of Concept

```json
// Caller submits to verify_foreign_transaction:
{
  "request": {
    "request": {
      "Bitcoin": {
        "tx_id": "<32-byte tx with 1 confirmation>",
        "confirmations": 0,
        "extractors": ["BlockHash"]
      }
    },
    "domain_id": <foreign_tx_domain_id>,
    "payload_version": 1
  }
}
```

The contract accepts this (deposit = 1 yoctonear, chain is supported). Each MPC node executes:

```rust
// bitcoin/inspector.rs line 51-52
let enough_block_confirmations = 0 <= transaction_block_confirmation; // always true
```

The node proceeds to `verify_block_is_canonical`, succeeds (transaction is in a block), and produces a signature share. Once threshold shares are collected, the contract returns a valid `VerifyForeignTransactionResponse` with a threshold signature over a payload encoding `confirmations: 0`. A bridge contract that trusts this signature will release funds for a transaction that has not reached any meaningful Bitcoin finality. [5](#0-4) [6](#0-5)

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
