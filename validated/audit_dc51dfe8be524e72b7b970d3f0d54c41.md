### Title
No Minimum Confirmation Count Enforced in `verify_foreign_transaction` for Bitcoin Requests - (File: `crates/contract/src/lib.rs`)

### Summary
The `verify_foreign_transaction` contract method accepts `BitcoinRpcRequest` with any caller-supplied `confirmations` value, including `0` or `1`, without enforcing a protocol-level minimum. The MPC network will sign a payload attesting to a Bitcoin transaction that has not reached a safe finality depth. A bridge contract that trusts the MPC layer to enforce finality — rather than re-checking the `confirmations` field in the signed payload — can be exploited for a double-spend: the attacker obtains a valid MPC signature over a barely-confirmed transaction, claims bridge funds, then reorganizes the Bitcoin chain to erase the original deposit.

### Finding Description
`verify_foreign_transaction` in `crates/contract/src/lib.rs` performs four precondition checks before enqueuing the request:

1. Domain exists and has `ForeignTx` purpose
2. Sufficient prepaid gas
3. Sufficient deposit
4. Chain is in the supported-chains whitelist [1](#0-0) 

None of these checks inspect the `confirmations` field inside `BitcoinRpcRequest`. The field is accepted verbatim and stored in the pending request.

On the node side, `execute_foreign_chain_request` in `crates/node/src/providers/verify_foreign_tx/sign.rs` forwards the user-supplied `confirmations` value directly to the Bitcoin inspector as the finality threshold: [2](#0-1) 

The inspector enforces `actual_confirmations >= threshold` — but when `threshold = 0` (or `1`), this check is trivially satisfied by any transaction that has appeared on-chain at all. The signed `ForeignTxSignPayloadV1` embeds the full `ForeignChainRpcRequest` (including the low `confirmations` value): [3](#0-2) 

So the MPC network produces a cryptographically valid signature over a payload that attests to a transaction with only 1 (or 0) Bitcoin confirmations. The `confirmations` value is present in the signed blob, but a bridge contract that assumes the MPC layer enforces a safe minimum will not re-validate it.

### Impact Explanation
**High — double-spend / invalid bridge execution.**

An attacker who controls a Bitcoin transaction can:
1. Broadcast a deposit transaction to the Bitcoin network.
2. Wait for 1 confirmation (or even 0 if the RPC returns mempool entries).
3. Call `verify_foreign_transaction` with `confirmations: 1`.
4. Receive a valid MPC signature over `ForeignTxSignPayloadV1 { request: Bitcoin { confirmations: 1, … }, values: [BlockHash(…)] }`.
5. Submit the signature to a bridge contract to claim the bridged funds.
6. Simultaneously attempt a Bitcoin chain reorganization to erase the original deposit transaction.

If the bridge contract does not independently verify that `confirmations >= 6` (the standard Bitcoin finality threshold) in the signed payload, the attacker double-spends: they receive bridged funds on NEAR while the Bitcoin deposit is rolled back. This maps directly to the "double-spend conditions" and "invalid bridge execution" impact class.

### Likelihood Explanation
**Medium.** The `verify_foreign_transaction` feature is explicitly designed for bridge use-cases (the design document names "Omnibridge inbound flow" as the primary use case). Bridge contracts that integrate this feature may reasonably assume the MPC layer enforces a safe finality floor — especially because the contract already enforces other safety invariants (chain whitelist, domain purpose, deposit). A developer who reads the API and sees `confirmations` as a user-supplied field may still omit the downstream check, believing the MPC network acts as the finality oracle. The attacker entry path requires no special privilege: any NEAR account can call `verify_foreign_transaction` with a 1-yoctoNEAR deposit.

### Recommendation
Enforce a configurable minimum confirmation count for Bitcoin requests at the contract level, analogous to how `ChainEntry` validation rejects `quorum: 0`:

```rust
// In verify_foreign_transaction, before enqueuing:
if let ForeignChainRpcRequest::Bitcoin(ref btc) = request.request {
    let min = self.config.bitcoin_min_confirmations; // e.g. 6
    if btc.confirmations.0 < min {
        env::panic_str("Bitcoin confirmations below protocol minimum");
    }
}
```

Alternatively, add a `min_confirmations` field to `ChainEntry` for Bitcoin so participants can vote on the floor value alongside the RPC provider list. At minimum, document prominently that `confirmations` is caller-controlled and that every consuming bridge contract **must** re-validate the field in the returned `ForeignTxSignPayloadV1`.

### Proof of Concept
```
# 1. Broadcast a Bitcoin deposit transaction; wait for 1 confirmation.
# 2. Call verify_foreign_transaction with confirmations: 1
near call <mpc_contract> verify_foreign_transaction '{
  "request": {
    "request": {
      "Bitcoin": {
        "tx_id": "<deposit_txid>",
        "confirmations": 1,
        "extractors": ["BlockHash"]
      }
    },
    "domain_id": <foreign_tx_domain>,
    "payload_version": 1
  }
}' --deposit 1 --gas 300000000000000

# 3. MPC nodes verify actual_confirmations (1) >= threshold (1) → pass.
#    Nodes sign ForeignTxSignPayloadV1 { request: { confirmations: 1 }, values: [BlockHash] }.

# 4. Bridge contract receives the valid MPC signature and releases funds
#    without checking that confirmations >= 6.

# 5. Attacker broadcasts a conflicting Bitcoin transaction (double-spend)
#    before the original reaches 6 confirmations.
```

The contract-level gap is at `crates/contract/src/lib.rs` lines 519–557 (no `confirmations` floor check) and the node-level gap is at `crates/node/src/providers/verify_foreign_tx/sign.rs` lines 117–130 (threshold passed through verbatim from user input). [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L117-130)
```rust
    async fn execute_foreign_chain_request(
        &self,
        request: &dtos::ForeignChainRpcRequest,
        payload_version: dtos::ForeignTxPayloadVersion,
    ) -> anyhow::Result<dtos::ForeignTxSignPayload> {
        chain_is_supported(&self.foreign_chain_policy_reader, request).await?;

        let values: Vec<dtos::ExtractedValue> = match request {
            dtos::ForeignChainRpcRequest::Ethereum(_request) => {
                bail!("ForeignChainRpcRequest::Ethereum is unsupported")
            }
            dtos::ForeignChainRpcRequest::Solana(_request) => {
                bail!("ForeignChainRpcRequest::Solana is unsupported")
            }
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1502)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```
