### Title
`GetTransactionReceiptResponse.status` Declared as Non-Optional `U64` Causes Deserialization Failure for EVM Transactions Without a Status Field — (File: `crates/foreign-chain-rpc-interfaces/src/evm.rs`)

---

### Summary

The `status` field in `GetTransactionReceiptResponse` is declared as a required, non-optional `U64`. Per the Ethereum JSON-RPC specification, `status` is absent (`null`) for pre-Byzantium (pre-EIP-658) transactions. When any MPC node queries such a transaction via `eth_getTransactionReceipt`, the `serde` deserialization of the response fails because `null` cannot be coerced into `U64`. This causes every participating node to error out and produce no signature share, permanently breaking the `verify_foreign_transaction` request lifecycle for that transaction class.

---

### Finding Description

In `crates/foreign-chain-rpc-interfaces/src/evm.rs`, the partial response type for `eth_getTransactionReceipt` is:

```rust
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GetTransactionReceiptResponse {
    pub block_hash: H256,
    pub block_number: U64,
    pub status: U64,   // ← non-optional
    pub logs: Vec<Log>,
}
``` [1](#0-0) 

The Ethereum JSON-RPC specification (EIP-658, Byzantium hard fork, block 4,370,000) introduced the `status` field. For any transaction mined **before** that block, the field is `null` in the RPC response. Because `status` is typed as `U64` (not `Option<U64>`), `serde_json` returns a deserialization error when it encounters `null`, which jsonrpsee wraps as a `ClientError`.

In `crates/foreign-chain-inspector/src/evm/inspector.rs`, the receipt is fetched with:

```rust
let transaction_receipt: GetTransactionReceiptResponse = self
    .client
    .request(GET_TRANSACTION_RECEIPT_METHOD, &get_transaction_receipt_args)
    .await?;
``` [2](#0-1) 

The `?` propagates the deserialization error as `ForeignChainInspectionError::ClientError` (via the `#[from]` derive on `ClientError`): [3](#0-2) 

The `status` field is also the sole gate for transaction-success verification:

```rust
let transaction_success = transaction_receipt.status == U64::one();
if !transaction_success {
    return Err(ForeignChainInspectionError::TransactionFailed);
}
``` [4](#0-3) 

Because deserialization fails before this check is reached, the node cannot distinguish "transaction failed" from "status field absent" — both result in the node not producing a signature share.

The same `EvmInspector` is shared across all EVM-compatible chains supported by the system (Ethereum, Base, BNB, Arbitrum, Polygon, HyperEVM, Abstract): [5](#0-4) 

---

### Impact Explanation

When a `verify_foreign_transaction` request targets a pre-Byzantium EVM transaction (or any EVM-compatible chain that omits `status`), every MPC node's `EvmInspector::extract()` call fails at deserialization. No node produces a signature share. Per the documented failure behavior:

> "A failed verification does **not** produce an on-chain failure response. The request eventually times out and fails with the standard timeout error." [6](#0-5) 

For bridge contracts (the primary use case of `verify_foreign_transaction`) that lock funds before calling `verify_foreign_transaction` and rely on the response to release them, a permanent timeout means those funds are permanently frozen. This matches the **Medium** allowed impact: *request-lifecycle manipulation that breaks production safety/accounting invariants*.

---

### Likelihood Explanation

An unprivileged caller can submit any `verify_foreign_transaction` request with any EVM transaction ID. Pre-Byzantium Ethereum transactions are publicly queryable. Additionally, some EVM-compatible chains in the supported set may have non-standard receipt formats that omit `status`. The attacker entry path requires only a valid NEAR account and 1 yoctoNEAR deposit — no privileged access.

---

### Recommendation

Change `status` to `Option<U64>` in `GetTransactionReceiptResponse`:

```rust
pub struct GetTransactionReceiptResponse {
    pub block_hash: H256,
    pub block_number: U64,
    pub status: Option<U64>,  // null for pre-Byzantium transactions
    pub logs: Vec<Log>,
}
```

In `EvmInspector::extract()`, handle the `None` case explicitly — either by rejecting pre-Byzantium transactions with a typed error (e.g., `ForeignChainInspectionError::MalformedRpcResponse`) or by treating absent `status` as a non-success:

```rust
let transaction_success = match transaction_receipt.status {
    Some(s) => s == U64::one(),
    None => return Err(ForeignChainInspectionError::MalformedRpcResponse(
        "status field absent (pre-Byzantium transaction)".to_string(),
    )),
};
```

---

### Proof of Concept

1. Identify any Ethereum mainnet transaction mined before block 4,370,000 (e.g., any transaction from 2015–2017). Its `eth_getTransactionReceipt` response will contain `"status": null`.

2. Submit a `verify_foreign_transaction` call to the MPC contract with that transaction ID and `EvmExtractor::BlockHash`.

3. Every MPC node's `EvmInspector::extract()` will attempt to deserialize the receipt. `serde_json` will fail to parse `null` as `U64` for the `status` field, returning a `ClientError`.

4. No node produces a signature share. The on-chain yield times out. Any bridge contract that locked funds awaiting this response cannot release them.

### Citations

**File:** crates/foreign-chain-rpc-interfaces/src/evm.rs (L11-18)
```rust
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GetTransactionReceiptResponse {
    pub block_hash: H256,
    pub block_number: U64,
    pub status: U64,
    pub logs: Vec<Log>,
}
```

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L40-48)
```rust
impl<Client, Chain> ForeignChainInspector for EvmInspector<Client, Chain>
where
    Client: ClientT + Send + Sync,
    Chain: EvmChain + Send + Sync,
{
    type TransactionId = Chain::TransactionHash;
    type Finality = EthereumFinality;
    type Extractor = EvmExtractor;
    type ExtractedValue = EvmExtractedValue<Chain>;
```

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L59-65)
```rust
        let transaction_receipt: GetTransactionReceiptResponse = self
            .client
            .request(
                GET_TRANSACTION_RECEIPT_METHOD,
                &get_transaction_receipt_args,
            )
            .await?;
```

**File:** crates/foreign-chain-inspector/src/evm/inspector.rs (L75-79)
```rust
        let transaction_success = transaction_receipt.status == U64::one();

        if !transaction_success {
            return Err(ForeignChainInspectionError::TransactionFailed);
        }
```

**File:** crates/foreign-chain-inspector/src/lib.rs (L214-217)
```rust
pub enum ForeignChainInspectionError {
    #[error("inner network client failed to fetch")]
    ClientError(#[from] jsonrpsee::core::client::error::Error),
    /// Transient provider failure (transport error, timeout, rate limit, 5xx).
```

**File:** docs/foreign-chain-transactions.md (L556-559)
```markdown

* Nodes **do not participate** if RPC queries fail or extraction fails.
* A failed verification does **not** produce an on-chain failure response. The request eventually times out and fails with the standard timeout error.
* *Known limitation:* a failed verification is not signalled explicitly — even when the failure reason is known (RPC sub-quorum, extraction error), the request just times out. Emitting an explicit failure so callers can react sooner is a desirable improvement, tracked in [#3477](https://github.com/near/mpc/issues/3477).
```
