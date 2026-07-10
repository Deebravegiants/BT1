The code is clear. Let me verify there are no other guards elsewhere in the pipeline.

### Title
Missing `log.removed` Guard in `EvmExtractor::extract_value` Allows MPC Signing of Reorged Log Entries — (`crates/foreign-chain-inspector/src/evm/inspector.rs`)

---

### Summary

`EvmExtractor::extract_value` locates a log by `log_index` only and returns it unconditionally. It never checks `log.removed`. Because the `removed` field is preserved verbatim through every conversion layer and Borsh-serialized into `ForeignTxSignPayloadV1`, the MPC network can be made to sign a payload that attests to a log that no longer exists on the canonical chain.

---

### Finding Description

The `EvmExtractor::Log` arm in `extract_value`:

```rust
EvmExtractor::Log { log_index } => {
    let target_index = ethereum_types::U64::from(*log_index);
    let log = rpc_response
        .logs
        .iter()
        .find(|log| log.log_index == target_index)   // ← only field checked
        .cloned()
        .ok_or(ForeignChainInspectionError::LogIndexOutOfBounds)?;

    Ok(EvmExtractedValue::Log(log))                  // ← log.removed never inspected
}
``` [1](#0-0) 

The `Log` struct carries a `removed: bool` field per the Ethereum JSON-RPC spec: [2](#0-1) 

`removed=true` means the log was part of a block that was reorganized away. The field is copied without modification through `log_to_evm_log`: [3](#0-2) 

It is then Borsh-serialized as part of `EvmLog` inside `ForeignTxSignPayloadV1.values`: [4](#0-3) [5](#0-4) 

The two existing guards do not cover this:

- **`verify_finality_level`** — checks that the receipt's block number is at or below the finalized head. Block-level only.
- **`verify_block_is_canonical`** — re-fetches the canonical block at `receipt_block_number` and compares hashes. Also block-level only. [6](#0-5) 

Neither guard inspects individual log attributes. A stale RPC index can serve a receipt whose `block_hash` matches the canonical block (so both guards pass) while still marking one or more logs as `removed=true` — a condition that arises when the block was briefly reorged out and the index was not fully refreshed before the block was re-adopted.

---

### Impact Explanation

The signed `ForeignTxSignPayloadV1` hash is computed over the full Borsh encoding of the payload, which includes `EvmLog.removed`. A payload containing a log with `removed=true` produces a distinct, valid MPC signature. Any bridge or contract that trusts this signature and does not independently re-verify `removed` will act on a log that no longer exists on the canonical chain — enabling forged foreign-chain verification and potentially invalid bridge execution or double-spend conditions.

This matches the **High** impact category: *forged foreign-chain verification / light-client-style verification bypass that causes invalid bridge execution*.

---

### Likelihood Explanation

The precondition is a stale BNB RPC provider that serves `removed=true` on a log whose parent block is still canonical. This requires a double-reorg (block reorged out, then re-adopted) with the index partially refreshed — the block hash updated but the per-log `removed` flag not cleared. This is an unusual but documented failure mode of EVM RPC providers under chain reorganizations. The attacker cannot force it, but can monitor for it and submit a verification request the moment the window opens. Likelihood is **low** but non-zero and non-theoretical.

---

### Recommendation

Add a `removed` guard immediately after the log is located:

```rust
EvmExtractor::Log { log_index } => {
    let target_index = ethereum_types::U64::from(*log_index);
    let log = rpc_response
        .logs
        .iter()
        .find(|log| log.log_index == target_index)
        .cloned()
        .ok_or(ForeignChainInspectionError::LogIndexOutOfBounds)?;

    if log.removed {
        return Err(ForeignChainInspectionError::RemovedLog);
    }

    Ok(EvmExtractedValue::Log(log))
}
```

Add a corresponding `RemovedLog` variant to `ForeignChainInspectionError` and a unit test that passes a receipt with `removed=true` and asserts the error is returned.

---

### Proof of Concept

Build a mock `EvmInspector` for `Bnb` with:

- `eth_getTransactionReceipt` → receipt with `status=1`, `block_hash=X`, `block_number=90`, `logs=[Log{removed:true, log_index:0, …}]`
- `eth_getBlockByNumber("finalized")` → `{number:100, hash:Y}` (finality passes)
- `eth_getBlockByNumber(90)` → `{number:90, hash:X}` (canonical check passes)

Call `inspector.extract(tx_id, Finalized, vec![EvmExtractor::Log{log_index:0}])`.

**Expected (with fix):** `Err(ForeignChainInspectionError::RemovedLog)`

**Actual (current code):** `Ok(vec![EvmExtractedValue::Log(Log{removed:true,…})])`

The resulting `ForeignTxSignPayloadV1` Borsh-encodes `removed=true` and produces a valid MPC signature over a log that does not exist on the canonical BNB chain. [7](#0-6) [8](#0-7)

### Citations

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L67-73)
```rust
        self.verify_finality_level(transaction_receipt.block_number, finality)
            .await?;
        self.verify_block_is_canonical(
            transaction_receipt.block_number,
            transaction_receipt.block_hash,
        )
        .await?;
```

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L174-195)
```rust
impl EvmExtractor {
    fn extract_value<Chain: EvmChain>(
        &self,
        rpc_response: &GetTransactionReceiptResponse,
    ) -> Result<EvmExtractedValue<Chain>, ForeignChainInspectionError> {
        match self {
            EvmExtractor::BlockHash => Ok(EvmExtractedValue::BlockHash(From::from(
                *rpc_response.block_hash.as_fixed_bytes(),
            ))),
            EvmExtractor::Log { log_index } => {
                let target_index = ethereum_types::U64::from(*log_index);
                let log = rpc_response
                    .logs
                    .iter()
                    .find(|log| log.log_index == target_index)
                    .cloned()
                    .ok_or(ForeignChainInspectionError::LogIndexOutOfBounds)?;

                Ok(EvmExtractedValue::Log(log))
            }
        }
    }
```

**File:** crates/foreign-chain-rpc-interfaces/src/evm.rs (L90-100)
```rust
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

**File:** crates/foreign-chain-inspector/src/contract_interface_conversions.rs (L58-74)
```rust
fn log_to_evm_log(value: Log) -> dtos::EvmLog {
    dtos::EvmLog {
        removed: value.removed,
        log_index: value.log_index.as_u64(),
        transaction_index: value.transaction_index.as_u64(),
        transaction_hash: dtos::Hash256(value.transaction_hash.0),
        block_hash: dtos::Hash256(value.block_hash.0),
        block_number: value.block_number.as_u64(),
        address: dtos::Hash160(value.address.0),
        data: value.data,
        topics: value
            .topics
            .into_iter()
            .map(|t| dtos::Hash256(t.0))
            .collect(),
    }
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L863-873)
```rust
pub struct EvmLog {
    pub removed: bool,
    pub log_index: u64,
    pub transaction_index: u64,
    pub transaction_hash: Hash256,
    pub block_hash: Hash256,
    pub block_number: u64,
    pub address: Hash160,
    pub data: String,
    pub topics: Vec<Hash256>,
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1502)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```

**File:** crates/foreign-chain-inspector/tests/evm_inspector.rs (L39-51)
```rust
fn test_log() -> Log {
    Log {
        removed: false,
        log_index: U64([1]),
        transaction_index: U64([2]),
        transaction_hash: H256([3; 32]),
        block_hash: H256([4; 32]),
        block_number: U64([5]),
        address: H160([6; 20]),
        data: "test_log".to_string(),
        topics: vec![H256([7; 32]), H256([8; 32])],
    }
}
```
