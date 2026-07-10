### Title
Missing Transaction Hash Binding in EVM Receipt Verification Enables Single-Provider Forgery for Non-Existent Transactions — (`crates/foreign-chain-inspector/src/evm/inspector.rs` + `crates/foreign-chain-rpc-interfaces/src/evm.rs`)

---

### Summary

`EvmInspector::extract` never verifies that the receipt returned by an RPC provider corresponds to the transaction hash that was requested. For a **non-existent** transaction hash, honest providers return JSON `null`, which jsonrpsee fails to deserialize into `GetTransactionReceiptResponse`, producing a `ClientError` — classified as **transient** by `ForeignChainInspectionError::is_transient`. The fan-out tolerates transient errors when any provider returns a substantive success. A single compromised provider can therefore return a receipt for a different, canonical, successful transaction and have it accepted as the verification result.

---

### Finding Description

**Missing field and missing check.**

`GetTransactionReceiptResponse` contains no `transactionHash` field: [1](#0-0) 

`EvmInspector::extract` sends the requested hash to the RPC, receives a receipt, and proceeds directly to finality and canonicality checks — never asserting that the receipt belongs to the queried hash: [2](#0-1) 

The Aptos inspector performs the equivalent check immediately after fetching: [3](#0-2) 

via: [4](#0-3) 

**Why null → transient.**

For a non-existent EVM transaction, `eth_getTransactionReceipt` returns JSON `null`. jsonrpsee attempts to deserialize `null` into the non-`Option` struct `GetTransactionReceiptResponse` and fails. The resulting error propagates via `?` and is caught by the blanket `From` impl: [5](#0-4) 

`ClientError` is explicitly transient: [6](#0-5) 

**Fan-out accepts one success over all-transient failures.**

The fan-out logic: if there are any successes and zero non-transient errors, it returns the success — transient errors are silently tolerated: [7](#0-6) 

This is confirmed by the test `fan_out__should_tolerate_transient_when_only_one_inspector_succeeds`: [8](#0-7) 

**Attack path (concrete):**

1. Attacker submits a NEAR sign request referencing `tx_hash_A`, a hash that does not exist on the target EVM chain.
2. The fan-out queries all configured providers with `tx_hash_A`.
3. Honest providers return `null` → jsonrpsee deserialization fails → `ClientError` → **transient** → tolerated.
4. The attacker's provider returns the receipt of `tx_hash_B` — a real, canonical, finalized, successful transaction.
5. `verify_finality_level` passes (block is finalized).
6. `verify_block_is_canonical` passes (block hash matches canonical chain).
7. `status == U64::one()` passes.
8. `extractor.extract_value(&transaction_receipt)` returns the log or block hash from `tx_hash_B`.
9. Fan-out: one success, zero non-transient errors → returns `Ok(extracted_value)`.
10. The MPC signs an observation that was never produced by `tx_hash_A`.

Note: this path does **not** work for a *failed* transaction (status=0), because honest providers return the receipt with `status=0`, causing `TransactionFailed` (non-transient), which triggers `InspectorResponseMismatch`. The exploitable case is specifically a **non-existent** transaction hash.

---

### Impact Explanation

A single compromised or attacker-controlled RPC provider can cause the MPC node to sign a foreign-chain observation that was never produced by the submitted transaction hash. This constitutes forged foreign-chain verification enabling invalid bridge execution or double-spend conditions — matching the High impact category.

---

### Likelihood Explanation

The attacker needs to control one RPC provider in the node's fan-out. RPC providers are third-party services; a node operator using a compromised or malicious provider (e.g., a provider whose API key was stolen, or a provider that is itself adversarial) satisfies this precondition without any threshold collusion. The attacker also needs one canonical successful transaction on the target chain whose block is finalized — trivially available on any live EVM chain. The preconditions are realistic.

---

### Recommendation

1. Add `transaction_hash: H256` to `GetTransactionReceiptResponse`, mirroring the `transactionHash` field present in the Ethereum JSON-RPC spec and already present on `Log`: [9](#0-8) 

2. In `EvmInspector::extract`, after deserializing the receipt, assert `receipt.transaction_hash == H256(transaction.into())` and return `ForeignChainInspectionError::InconsistentRpcResponse` (non-transient) on mismatch — exactly as `ensure_hash_matches` does for Aptos.

3. Consider whether a null receipt (non-existent transaction) should map to `TransactionNotFound` (non-transient) rather than `ClientError` (transient), so that honest providers' "not found" verdict is not silently discarded.

---

### Proof of Concept

```rust
// Deterministic unit test demonstrating the missing hash binding.
// A mock ClientT returns a receipt for HASH_B when queried for HASH_A.
// extract() returns Ok and the extracted log belongs to HASH_B, not HASH_A.

struct SubstitutingClient; // returns receipt of HASH_B for any query

#[tokio::test]
async fn evm_extract_accepts_receipt_for_different_hash() {
    let inspector = EvmInspector::<_, SomeChain>::new(SubstitutingClient);
    let tx_hash_a: [u8; 32] = [0xAA; 32]; // non-existent on chain
    let result = inspector
        .extract(tx_hash_a.into(), EthereumFinality::Finalized, vec![EvmExtractor::Log { log_index: 0 }])
        .await;
    // Passes today — receipt of HASH_B is accepted as verification of HASH_A.
    assert!(result.is_ok());
    // The extracted log carries transaction_hash == HASH_B, not HASH_A.
    if let Ok(vals) = result {
        if let EvmExtractedValue::Log(log) = &vals[0] {
            assert_ne!(log.transaction_hash.0, tx_hash_a); // demonstrates the substitution
        }
    }
}
```

### Citations

**File:** crates/foreign-chain-rpc-interfaces/src/evm.rs (L13-18)
```rust
pub struct GetTransactionReceiptResponse {
    pub block_hash: H256,
    pub block_number: U64,
    pub status: U64,
    pub logs: Vec<Log>,
}
```

**File:** crates/foreign-chain-rpc-interfaces/src/evm.rs (L88-100)
```rust
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Log {
    pub removed: bool,
    pub log_index: U64,
    pub transaction_index: U64,
    pub transaction_hash: H256,
    pub block_hash: H256,
    pub block_number: U64,
    pub address: H160,
    pub data: String,
    pub topics: Vec<H256>,
}
```

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L56-65)
```rust
        let get_transaction_receipt_args = GetTransactionReceiptARgs {
            transaction_hash: H256(transaction.into()),
        };
        let transaction_receipt: GetTransactionReceiptResponse = self
            .client
            .request(
                GET_TRANSACTION_RECEIPT_METHOD,
                &get_transaction_receipt_args,
            )
            .await?;
```

**File:** crates/foreign-chain-inspector/src/aptos/inspector.rs (L77-77)
```rust
        ensure_hash_matches(&tx_id, &tx.hash)?;
```

**File:** crates/foreign-chain-inspector/src/aptos/inspector.rs (L108-125)
```rust
fn ensure_hash_matches(
    requested: &[u8; 32],
    returned: &str,
) -> Result<(), ForeignChainInspectionError> {
    let returned_bytes =
        hex::decode(returned.strip_prefix("0x").unwrap_or(returned)).map_err(|e| {
            ForeignChainInspectionError::MalformedRpcResponse(format!(
                "non-hex transaction hash in response: {e}"
            ))
        })?;
    if returned_bytes.as_slice() != requested.as_slice() {
        return Err(ForeignChainInspectionError::InconsistentRpcResponse {
            requested_hash: HexBytes(requested.to_vec()),
            returned_hash: HexBytes(returned_bytes),
        });
    }
    Ok(())
}
```

**File:** crates/foreign-chain-inspector/src/lib.rs (L118-142)
```rust
        let inspectors_split_between_success_and_failure =
            !successes.is_empty() && !non_transient_errors.is_empty();

        if inspectors_split_between_success_and_failure {
            tracing::error!(
                ?successes,
                ?non_transient_errors,
                "fan-out: inspectors split between success and non-transient failure",
            );
            return Err(ForeignChainInspectionError::InspectorResponseMismatch);
        }

        if let Some(first_values) = successes.first() {
            let all_successes_agree = successes.iter().all(|(_, v)| v == &first_values.1);
            if !all_successes_agree {
                tracing::error!(
                    responses = ?successes,
                    "fan-out: inspectors returned mismatching extracted values",
                );
                return Err(ForeignChainInspectionError::InspectorResponseMismatch);
            }
            let (_, first) = successes.into_iter().next().expect("checked non-empty");

            return Ok(first);
        }
```

**File:** crates/foreign-chain-inspector/src/lib.rs (L216-216)
```rust
    ClientError(#[from] jsonrpsee::core::client::error::Error),
```

**File:** crates/foreign-chain-inspector/src/lib.rs (L266-274)
```rust
    pub fn is_transient(&self) -> bool {
        matches!(
            self,
            Self::ClientError(_)
                | Self::RpcRequestFailed(_)
                | Self::NotFinalized
                | Self::NotEnoughBlockConfirmations { .. }
        )
    }
```

**File:** crates/foreign-chain-inspector/tests/fanout.rs (L503-515)
```rust
    #[tokio::test]
    async fn fan_out__should_tolerate_transient_when_only_one_inspector_succeeds() {
        // Given
        let succeeding = mock_returning(ok(vec![99]));
        let make_transient = || mock_returning(err(|| ForeignChainInspectionError::NotFinalized));
        let fan_out = fan_out_of(vec![make_transient(), succeeding, make_transient()]);

        // When
        let result = fan_out.extract((), (), vec![]).await;

        // Then
        assert_eq!(result.unwrap(), vec![99]);
    }
```
