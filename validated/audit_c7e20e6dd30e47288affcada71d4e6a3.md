### Title
Unvalidated Caller-Controlled `confirmations` Parameter in `verify_foreign_transaction` Enables Bitcoin Finality Bypass — (`crates/contract/src/lib.rs`, `crates/foreign-chain-inspector/src/bitcoin/inspector.rs`)

---

### Summary

The `verify_foreign_transaction` contract method accepts a `BitcoinRpcRequest` whose `confirmations: BlockConfirmations` field is entirely caller-controlled and is never validated by the contract before the request is enqueued. The MPC node then uses this value verbatim as the finality threshold. Setting `confirmations = 0` causes the node-side check to trivially pass for any mined transaction, allowing the MPC network to produce a threshold signature attesting to a Bitcoin transaction that has not reached any meaningful finality.

---

### Finding Description

`verify_foreign_transaction` in `crates/contract/src/lib.rs` performs four checks before enqueuing a request: [1](#0-0) 

It validates domain purpose, gas, deposit, and chain membership — but **never inspects the contents of the chain-specific request struct**. For a `BitcoinRpcRequest`, the `confirmations` field (a plain `u64`, minimum 0 per the ABI schema) is passed through unchanged: [2](#0-1) 

On the node side, `execute_foreign_chain_request` in `crates/node/src/providers/verify_foreign_tx/sign.rs` forwards the caller-supplied value directly to the Bitcoin inspector as `block_confirmations_threshold`: [3](#0-2) 

The inspector's finality guard is: [4](#0-3) 

When `block_confirmations_threshold = 0`, the condition `0 <= actual_confirmations` is always true for any transaction that has been mined (even with a single confirmation). The guard is therefore completely bypassed, and the inspector proceeds to extract the block hash and return successfully.

The resulting `ForeignTxSignPayload::V1` embeds the full original request — including `confirmations = 0` — and the MPC network signs it: [5](#0-4) 

---

### Impact Explanation

The `verify_foreign_transaction` pathway exists specifically to let the MPC network act as a trusted finality oracle for foreign chains. By setting `confirmations = 0`, an unprivileged caller obtains a valid threshold signature attesting that a Bitcoin transaction was observed in a block — with no confirmation requirement whatsoever. A bridge contract consuming this signature cannot distinguish it from a legitimately finalized attestation unless it independently re-checks the `confirmations` field embedded in the signed payload. Any bridge that trusts the MPC attestation without re-validating that field is exposed to double-spend: the attacker's Bitcoin transaction can be reorganized out of the chain after the bridge has already released funds on the NEAR side.

This matches the allowed High impact: **forged foreign-chain verification / light-client-style verification bypass that causes invalid bridge execution or double-spend conditions**.

---

### Likelihood Explanation

The attack requires only:
1. A Bitcoin transaction that has been included in at least one block (1 confirmation).
2. A 1 yoctonear deposit and sufficient gas to call `verify_foreign_transaction`.
3. Setting `confirmations = 0` in the `BitcoinRpcRequest`.

No privileged access, collusion, or TEE compromise is needed. Any unprivileged NEAR account can execute this.

---

### Recommendation

Enforce a minimum `confirmations` value in `verify_foreign_transaction` before enqueuing the request, analogous to how the contract already validates domain purpose and chain membership:

```rust
// Inside verify_foreign_transaction, after chain membership check:
if let ForeignChainRpcRequest::Bitcoin(ref btc_req) = request.request {
    require!(
        btc_req.confirmations.0 >= MINIMUM_BITCOIN_CONFIRMATIONS,
        "Bitcoin confirmations below required minimum"
    );
}
```

Alternatively, encode the minimum per-chain confirmation threshold in the on-chain `ChainEntry` configuration (voted in by participants) so the contract can enforce it dynamically without a hard-coded constant.

---

### Proof of Concept

1. Attacker broadcasts a Bitcoin transaction; waits for 1 block confirmation.
2. Attacker calls `verify_foreign_transaction` with:
   ```json
   {
     "request": {
       "Bitcoin": {
         "tx_id": "<attacker_tx_id>",
         "confirmations": 0,
         "extractors": ["BlockHash"]
       }
     },
     "domain_id": <foreign_tx_domain>,
     "payload_version": 1
   }
   ```
3. MPC nodes query `getrawtransaction` — response includes `confirmations: 1`.
4. Node evaluates `0 <= 1` → `true`; finality guard passes.
5. Node signs `ForeignTxSignPayload::V1 { request: {…, confirmations: 0}, values: [block_hash] }`.
6. Attacker receives a valid MPC threshold signature over the 1-confirmation transaction.
7. Attacker submits the signature to a bridge contract to claim funds on NEAR.
8. Bitcoin miners reorganize the block; the original transaction disappears.
9. Bridge funds are already disbursed — double-spend complete.

### Citations

**File:** crates/contract/src/lib.rs (L526-542)
```rust
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
```

**File:** crates/contract/src/dto_mapping.rs (L840-848)
```rust
pub fn args_into_verify_foreign_tx_request(
    args: dtos::VerifyForeignTransactionRequestArgs,
) -> dtos::VerifyForeignTransactionRequest {
    dtos::VerifyForeignTransactionRequest {
        domain_id: args.domain_id,
        request: args.request,
        payload_version: args.payload_version,
    }
}
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L131-151)
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
            }
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L337-347)
```rust
        let payload = match payload_version {
            dtos::ForeignTxPayloadVersion::V1 => {
                dtos::ForeignTxSignPayload::V1(dtos::ForeignTxSignPayloadV1 {
                    request: request.clone(),
                    values,
                })
            }
            _ => bail!("unsupported payload_version"),
        };
        Ok(payload)
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
