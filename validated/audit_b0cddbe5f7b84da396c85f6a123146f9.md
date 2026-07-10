### Title
User-Controlled Finality Parameters in `verify_foreign_transaction` Enable Double-Spend Attacks - (File: `crates/contract/src/lib.rs`, `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`)

---

### Summary

The `verify_foreign_transaction` endpoint accepts user-controlled finality parameters (`confirmations` for Bitcoin, `finality` for EVM/Starknet) with no minimum enforced by the contract or protocol. An unprivileged caller can set these to the weakest possible values, causing the MPC network to produce a threshold signature attesting to a foreign-chain transaction that has not reached true finality. If the foreign chain subsequently reorgs that transaction, the MPC signature remains valid and can be replayed to claim bridge funds, constituting a double-spend.

---

### Finding Description

`verify_foreign_transaction` accepts a `VerifyForeignTransactionRequestArgs` struct that includes a chain-specific `ForeignChainRpcRequest`. For Bitcoin this struct carries a user-supplied `confirmations: BlockConfirmations` field; for EVM chains it carries a user-supplied `finality: EvmFinality` (variants: `Latest`, `Safe`, `Finalized`); for Starknet a user-supplied `StarknetFinality` (`Processed`, `Confirmed`, `Finalized`).

The contract's `verify_foreign_transaction` method performs only four checks before enqueuing the request:

1. The domain exists and has `ForeignTx` purpose.
2. Sufficient prepaid gas.
3. Deposit ≥ 1 yoctonear.
4. The requested chain is in the supported set. [1](#0-0) 

None of these checks constrain the finality level or minimum confirmation count. The user-supplied value flows directly into the pending request store and is later consumed by MPC nodes when they query the foreign chain. [2](#0-1) 

On the node side, `execute_foreign_chain_request` passes the user-supplied `request` (including its finality/confirmation field) verbatim to the chain-specific inspector: [3](#0-2) 

The inspector then queries the RPC provider and checks that the transaction satisfies the caller-chosen finality level. If it does, all threshold-many nodes independently reach the same conclusion and the coordinator submits a `respond_verify_foreign_tx` call, producing a valid MPC threshold signature over the `ForeignTxSignPayload`. [4](#0-3) 

The signed payload encodes the original request (including the user-chosen finality parameter) and the extracted values: [5](#0-4) 

Because the MPC signature is over `SHA-256(borsh(ForeignTxSignPayload))`, and the payload includes the user-chosen finality level, the signature is permanently valid even if the foreign chain later reorgs the transaction.

---

### Impact Explanation

A malicious bridge user submits `verify_foreign_transaction` with `confirmations: 1` (Bitcoin) or `finality: Latest` (EVM). The MPC network, operating correctly under the user-supplied parameters, produces a valid threshold signature attesting that the transaction occurred. The user presents this signature to the NEAR bridge contract to claim funds. The user then double-spends the Bitcoin/EVM transaction (exploiting the shallow confirmation depth or a reorg). The bridge has already released funds on NEAR based on the MPC signature, which remains cryptographically valid. This is a direct, concrete double-spend: funds are lost from the bridge with no recourse, because the MPC signature cannot be revoked.

This matches the allowed impact: **"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass … that causes invalid bridge execution or double-spend conditions."**

---

### Likelihood Explanation

The attack requires only a 1 yoctonear deposit and standard NEAR gas. No privileged access, threshold collusion, or key material is needed. The attacker simply submits a well-formed `verify_foreign_transaction` call with a minimal finality parameter. Bitcoin 1-confirmation reorgs occur in practice; EVM `Latest`-block reorgs are routine during network congestion. The attack is economically rational whenever the bridge value exceeds the cost of executing a reorg on the foreign chain (or when a natural reorg occurs opportunistically).

---

### Recommendation

The contract should enforce a protocol-defined minimum finality level for each supported chain, set by participant governance (analogous to how the RPC provider whitelist is governed). Concretely:

- Store a per-chain `MinFinality` configuration in `ForeignChainsMetadata`, voteable by participants via the existing governance mechanism.
- In `verify_foreign_transaction`, after the chain-support check, validate that the user-supplied finality/confirmation value meets or exceeds the stored minimum.
- Reject requests that specify weaker finality than the protocol minimum, returning a clear error.

This mirrors the external report's recommendation: the security-critical parameter must not be derived from user input but must be set by an authorized governance process.

---

### Proof of Concept

1. Participants vote to add Bitcoin to the supported foreign chain set with a `ForeignTx` domain.
2. Attacker deposits 1 BTC to the NEAR bridge, triggering a Bitcoin transaction `TX_A`.
3. Attacker calls `verify_foreign_transaction` with:
   ```json
   {
     "request": {
       "Bitcoin": {
         "tx_id": "<TX_A>",
         "confirmations": 1,
         "extractors": ["BlockHash"]
       }
     },
     "domain_id": <foreign_tx_domain>,
     "payload_version": "V1"
   }
   ```
   with `deposit: 1 yoctonear`.
4. After 1 Bitcoin confirmation, all MPC nodes independently verify the transaction and the coordinator calls `respond_verify_foreign_tx`, producing a valid threshold signature.
5. Attacker presents the signature to the NEAR bridge contract, which releases 1 BTC-equivalent in wrapped tokens.
6. Attacker simultaneously broadcasts a conflicting Bitcoin transaction double-spending `TX_A`. With only 1 confirmation, a miner with sufficient hashrate (or a natural reorg) can reverse `TX_A`.
7. The MPC signature remains valid; the bridge has already paid out. Net loss: bridge funds equal to the deposit amount.

The root cause — user-controlled `confirmations` accepted without a protocol-enforced minimum — is directly analogous to the external report's user-controlled `volatility` parameter: in both cases, a user-supplied value that should be set by the protocol is instead freely chosen by the caller to their own advantage. [6](#0-5) [2](#0-1)

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L84-105)
```rust
#[derive(
    Debug,
    Clone,
    Eq,
    PartialEq,
    Ord,
    PartialOrd,
    Hash,
    Serialize,
    Deserialize,
    BorshSerialize,
    BorshDeserialize,
)]
#[cfg_attr(
    all(feature = "abi", not(target_arch = "wasm32")),
    derive(schemars::JsonSchema, borsh::BorshSchema)
)]
pub struct VerifyForeignTransactionRequestArgs {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L73-87)
```rust
        let response_payload = self
            .execute_foreign_chain_request(
                &foreign_tx_request.request,
                foreign_tx_request.payload_version,
            )
            .await?;

        let sign_request = build_signature_request(&foreign_tx_request, &response_payload)?;

        let response = self
            .ecdsa_signature_provider
            .make_signature_leader_given_parameters(sign_request, presignature, channel)
            .await?;
        Ok(((response_payload, response.0), response.1))
    }
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L117-125)
```rust
    async fn execute_foreign_chain_request(
        &self,
        request: &dtos::ForeignChainRpcRequest,
        payload_version: dtos::ForeignTxPayloadVersion,
    ) -> anyhow::Result<dtos::ForeignTxSignPayload> {
        chain_is_supported(&self.foreign_chain_policy_reader, request).await?;

        let values: Vec<dtos::ExtractedValue> = match request {
            dtos::ForeignChainRpcRequest::Ethereum(_request) => {
```
