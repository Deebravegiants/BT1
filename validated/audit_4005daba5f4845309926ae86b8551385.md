### Title
Caller-Controlled `finality: Latest` in `verify_foreign_transaction` Enables MPC Attestation of Reorganizable Transactions — (File: `crates/contract/src/lib.rs`)

---

### Summary

The `verify_foreign_transaction` contract method accepts any finality level from an unprivileged caller, including `EthereumFinality::Latest` — the weakest, analogous to reading `slot0()` (spot price) in the external report. An attacker can obtain a valid MPC threshold signature attesting to a foreign-chain transaction that has not yet reached economic finality. If the transaction's block is subsequently reorganized (a realistic event on Polygon, BNB, and other supported EVM chains), the attacker holds a valid MPC attestation for a transaction that no longer exists on the foreign chain, enabling a double-spend against any bridge or application that trusts the attestation.

---

### Finding Description

**Root cause — no minimum finality enforcement in `verify_foreign_transaction`:**

The function validates that the requested chain is supported but imposes no minimum finality level on the caller-supplied `finality` field inside `EvmRpcRequest`. [1](#0-0) 

The `finality` field flows directly into `execute_foreign_chain_request`, which dispatches to the EVM inspector's `verify_finality_level`: [2](#0-1) 

With `finality: Latest`, `verify_finality_level` queries `eth_getBlockByNumber("latest")` and checks only that the latest block number ≥ the receipt block number — a check that trivially passes for any transaction included in any block: [3](#0-2) 

The `EthereumFinality::Latest` variant is explicitly supported and accepted without restriction: [4](#0-3) 

The MPC network then signs a `ForeignTxSignPayloadV1` encoding `(request, observed_values)`, where `request` carries `finality: Latest`. The signed payload does include the finality field, so a well-implemented downstream contract could reject it — but the MPC contract itself provides no enforcement, and downstream contracts that only verify the signature and extracted values (e.g., block hash) without checking the finality level are fully exposed. [5](#0-4) 

**Analog mapping:**

| External Report (stNXM) | NEAR MPC Analog |
|---|---|
| `slot0()` reads current spot price | `finality: Latest` reads current chain head |
| Attacker swaps to inflate pool price | Attacker submits tx, requests attestation before finality |
| `totalAssets()` uses inflated price | Bridge uses MPC attestation for unfinalized tx |
| Withdrawal at inflated rate | Claim bridged tokens for a tx that gets reorganized |
| Fix: replace `slot0()` with TWAP | Fix: enforce `finality: Finalized` minimum |

**Attack path:**

1. Attacker sends a deposit transaction on a supported EVM chain (e.g., Polygon) to a bridge contract.
2. Transaction is included in a block (1 confirmation, `Latest` finality).
3. Attacker immediately calls `verify_foreign_transaction` with `finality: Latest` and the deposit `tx_id`.
4. MPC nodes each query their RPC provider, observe the transaction at `Latest` finality, extract values, and produce signature shares.
5. Threshold signature is assembled and returned on-chain.
6. Attacker submits the MPC attestation to the NEAR bridge → receives bridged tokens.
7. A reorg on the foreign chain (natural or induced) removes the deposit transaction.
8. Attacker holds bridged tokens on NEAR; the original deposit no longer exists on the foreign chain.

---

### Impact Explanation

This is a **forged foreign-chain verification** enabling **double-spend / invalid bridge execution**. The MPC network produces a valid threshold signature attesting to a transaction state that is subsequently invalidated by a reorg. Any bridge or application that trusts the MPC attestation without independently enforcing a minimum finality level will release funds for a deposit that no longer exists on the foreign chain.

This matches the allowed **High** impact: *"Cross-chain replay, forged foreign-chain verification, light-client-style verification bypass, or participant/attestation authorization bypass that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

The attack is reachable by any unprivileged caller — no privileged access, no key material, no threshold collusion required. The external precondition (a block reorganization) is realistic on several supported chains:

- **Polygon**: 1–2 block reorgs occur regularly; the network has experienced reorgs of up to 157 blocks historically.
- **BNB Chain**: reorgs of 1–3 blocks are not uncommon.
- **Arbitrum/Base**: sequencer-level reorgs are possible within the sequencer's finality window.

The attacker does not need to *cause* the reorg — they only need to submit the `verify_foreign_transaction` request during the window before the transaction's block is finalized, then wait for a natural reorg. On Polygon, this window spans several seconds to minutes. The attack is probabilistic but realistic, especially for high-value bridge deposits where the attacker is incentivized to wait.

---

### Recommendation

Enforce a minimum finality level in `verify_foreign_transaction` — directly analogous to replacing `slot0()` with TWAP:

```rust
// In verify_foreign_transaction, before enqueue_yield_request:
match &request.request {
    ForeignChainRpcRequest::Abstract(r) | ForeignChainRpcRequest::Bnb(r) | ... => {
        if matches!(r.finality, EvmFinality::Latest) {
            env::panic_str("finality: Latest is not permitted; use Safe or Finalized");
        }
    }
    _ => {}
}
```

Preferred fix: reject `finality: Latest` (and optionally `finality: Safe`) at the contract level for all EVM chains, requiring `finality: Finalized`. This prevents any caller from obtaining an MPC attestation for a non-finalized transaction, regardless of downstream contract behavior.

---

### Proof of Concept

```
1. Deploy a NEAR bridge contract that accepts MPC attestations from verify_foreign_transaction.
2. Send a deposit transaction on Polygon (tx_id = X).
3. Wait for 1 block confirmation (Latest finality satisfied).
4. Call verify_foreign_transaction:
   {
     "request": {
       "Polygon": {
         "tx_id": "X",
         "finality": "Latest",
         "extractors": ["BlockHash"]
       }
     },
     "domain_id": <foreign_tx_domain_id>,
     "payload_version": 1
   }
5. Receive valid MPC threshold signature over (request, [BlockHash(H)]).
6. Submit attestation to NEAR bridge → receive bridged tokens.
7. Wait for natural 1-block reorg on Polygon that removes tx X
   (or induce one via MEV/selfish mining on a low-hashrate window).
8. Attacker holds bridged tokens; bridge has lost funds with no recourse.
```

The `verify_foreign_transaction` function at `crates/contract/src/lib.rs:519` accepts the request without any finality-level gate, and `verify_finality_level` at `crates/foreign-chain-inspector/src/evm/inspector.rs:102` trivially passes for any block-included transaction when `Latest` is requested. [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L519-542)
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
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L30-48)
```rust
fn build_signature_request(
    request: &VerifyForeignTxRequest,
    foreign_tx_payload: &dtos::ForeignTxSignPayload,
) -> anyhow::Result<SignatureRequest> {
    let payload_hash: [u8; ECDSA_PAYLOAD_SIZE_BYTES] =
        foreign_tx_payload.compute_msg_hash()?.into();
    let payload_bytes: BoundedVec<u8, ECDSA_PAYLOAD_SIZE_BYTES, ECDSA_PAYLOAD_SIZE_BYTES> =
        payload_hash.into();

    Ok(SignatureRequest {
        id: request.id,
        receipt_id: request.receipt_id,
        payload: Payload::Ecdsa(payload_bytes),
        tweak: Tweak::new([0u8; 32]),
        entropy: request.entropy,
        timestamp_nanosec: request.timestamp_nanosec,
        domain: request.domain_id,
    })
}
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L117-122)
```rust
    async fn execute_foreign_chain_request(
        &self,
        request: &dtos::ForeignChainRpcRequest,
        payload_version: dtos::ForeignTxPayloadVersion,
    ) -> anyhow::Result<dtos::ForeignTxSignPayload> {
        chain_is_supported(&self.foreign_chain_policy_reader, request).await?;
```

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L102-125)
```rust
    async fn verify_finality_level(
        &self,
        receipt_block_number: U64,
        finality: EthereumFinality,
    ) -> Result<(), ForeignChainInspectionError> {
        let finality_tag = match finality {
            EthereumFinality::Finalized => FinalityTag::Finalized,
            EthereumFinality::Safe => FinalityTag::Safe,
            EthereumFinality::Latest => FinalityTag::Latest,
        };
        let args = GetBlockByNumberArgs::new(
            BlockNumberOrTag::Tag(finality_tag),
            ReturnFullTransactionObjects::from(false),
        );
        let head: GetBlockByNumberResponse = self
            .client
            .request(GET_BLOCK_BY_NUMBER_METHOD, &args)
            .await?;

        if head.number < receipt_block_number {
            return Err(ForeignChainInspectionError::NotFinalized);
        }
        Ok(())
    }
```

**File:** crates/foreign-chain-inspector/src/lib.rs (L207-211)
```rust
pub enum EthereumFinality {
    Finalized,
    Safe,
    Latest,
}
```
