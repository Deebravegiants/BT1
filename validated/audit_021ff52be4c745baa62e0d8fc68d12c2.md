Now I have enough context to make a determination. Let me verify the exact signing flow to confirm whether follower nodes independently compute the hash.

I now have a complete picture of the vulnerability. Here is my assessment:

---

### Title
`EvmLog.data` String Non-Normalization Causes Divergent `compute_msg_hash()` Across Nodes — (`crates/foreign-chain-inspector/src/contract_interface_conversions.rs`, `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`)

### Summary

`EvmLog.data` is typed as `String` and copied verbatim from the RPC JSON response into `ForeignTxSignPayloadV1`. Because Borsh serializes `String` as length-prefixed UTF-8 bytes, two nodes that receive the same log data in different hex representations (e.g., `"0xDEADBEEF"` vs `"0xdeadbeef"`) will produce different `compute_msg_hash()` outputs, causing threshold signing to fail for any EVM-family chain (BNB, Base, Arbitrum, Polygon, HyperEVM, Abstract) when the `Log` extractor is used.

### Finding Description

**Root cause — no normalization at any layer:**

`Log.data` in the RPC interface is a plain `String` with standard serde deserialization:

```rust
// crates/foreign-chain-rpc-interfaces/src/evm.rs:88-100
pub struct Log {
    ...
    pub data: String,   // raw JSON string, no normalization
    ...
}
``` [1](#0-0) 

`log_to_evm_log` copies it verbatim into the contract DTO:

```rust
// crates/foreign-chain-inspector/src/contract_interface_conversions.rs:58-74
fn log_to_evm_log(value: Log) -> dtos::EvmLog {
    dtos::EvmLog {
        ...
        data: value.data,   // ← no normalization
        ...
    }
}
``` [2](#0-1) 

`EvmLog.data` in the contract interface is `String` with `BorshSerialize`:

```rust
// crates/near-mpc-contract-interface/src/types/foreign_chain.rs:863-873
pub struct EvmLog {
    ...
    pub data: String,   // BorshSerialize encodes raw UTF-8 bytes
    ...
}
``` [3](#0-2) 

`compute_msg_hash()` Borsh-serializes the entire payload and SHA-256 hashes it:

```rust
// crates/near-mpc-contract-interface/src/types/foreign_chain.rs:1504-1509
pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
    let mut hasher = sha2::Sha256::new();
    borsh::BorshSerialize::serialize(self, &mut hasher)?;
    Ok(Hash256(hasher.finalize().into()))
}
``` [4](#0-3) 

**Both leader and follower independently compute the hash from their own RPC query:**

```rust
// crates/node/src/providers/verify_foreign_tx/sign.rs:73-80 (leader)
let response_payload = self.execute_foreign_chain_request(...).await?;
let sign_request = build_signature_request(&foreign_tx_request, &response_payload)?;

// crates/node/src/providers/verify_foreign_tx/sign.rs:103-110 (follower)
let response_payload = self.execute_foreign_chain_request(...).await?;
let sign_request = build_signature_request(&foreign_tx_request, &response_payload)?;
``` [5](#0-4) 

`build_signature_request` calls `compute_msg_hash()` and uses the result as the ECDSA signing payload: [6](#0-5) 

If node A's RPC returns `"0xDEADBEEF"` and node B's returns `"0xdeadbeef"`, Borsh encodes them as different byte sequences (different UTF-8 content), producing different SHA-256 hashes. The threshold signing protocol then fails because leader and follower are signing different messages.

### Impact Explanation

Any `verify_foreign_transaction` request for BNB (or any supported EVM chain) that includes `EvmExtractor::Log` will permanently fail to reach threshold if the nodes' RPC providers return different hex case for the same log data field. The request is consumed from the contract's pending queue on timeout, and the user's attached deposit is not refunded. This is a request-lifecycle freeze matching the Medium impact scope.

### Likelihood Explanation

The Ethereum JSON-RPC spec (EIP-1474) recommends lowercase hex but does not mandate it for the `data` field in log entries. Different providers (e.g., QuickNode, Alchemy, Infura, self-hosted nodes) have historically differed in hex case for data fields. A production deployment using different RPC providers per node — which is standard practice for redundancy — is directly exposed. The attacker only needs to submit a `verify_foreign_transaction` request for a BNB transaction whose receipt log data is returned with different case by different providers; no privileged access is required.

### Recommendation

Normalize `EvmLog.data` to a canonical form (lowercase `0x`-prefixed hex) at the point of deserialization or in `log_to_evm_log`, before the value enters `ForeignTxSignPayloadV1`. The same normalization should be applied to all string-typed fields that represent hex data (e.g., `topics` are already typed as `Hash256` byte arrays and are safe; only `data` is affected). A custom `serde` deserializer or a post-deserialization normalization step in `log_to_evm_log` would fix this.

### Proof of Concept

```rust
use near_mpc_contract_interface::types::{
    EvmLog, Hash256, Hash160, EvmExtractedValue, ExtractedValue,
    ForeignTxSignPayload, ForeignTxSignPayloadV1, ForeignChainRpcRequest,
    EvmRpcRequest, EvmTxId, EvmFinality, EvmExtractor,
};

fn make_payload(data: &str) -> ForeignTxSignPayload {
    ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
        request: ForeignChainRpcRequest::Bnb(EvmRpcRequest {
            tx_id: EvmTxId([0xab; 32]),
            extractors: vec![EvmExtractor::Log { log_index: 0 }],
            finality: EvmFinality::Finalized,
        }),
        values: vec![ExtractedValue::EvmExtractedValue(
            EvmExtractedValue::Log(EvmLog {
                removed: false,
                log_index: 0,
                transaction_index: 0,
                transaction_hash: Hash256([0xcc; 32]),
                block_hash: Hash256([0xdd; 32]),
                block_number: 100,
                address: Hash160([0xee; 20]),
                data: data.to_string(),   // ← only difference
                topics: vec![],
            }),
        )],
    })
}

let hash_upper = make_payload("0xDEADBEEF").compute_msg_hash().unwrap();
let hash_lower = make_payload("0xdeadbeef").compute_msg_hash().unwrap();
assert_ne!(hash_upper, hash_lower);  // ← divergent hashes, threshold fails
```

### Citations

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1504-1509)
```rust
impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L30-47)
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
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L73-114)
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

    pub(super) async fn make_verify_foreign_tx_follower(
        &self,
        channel: NetworkTaskChannel,
        id: SignatureId,
        presignature_id: UniqueId,
    ) -> anyhow::Result<()> {
        metrics::MPC_NUM_PASSIVE_SIGN_REQUESTS_RECEIVED.inc();
        let foreign_tx_request = timeout(
            Duration::from_secs(self.config.signature.timeout_sec),
            self.verify_foreign_tx_request_store.get(id),
        )
        .await??;
        metrics::MPC_NUM_PASSIVE_SIGN_REQUESTS_LOOKUP_SUCCEEDED.inc();

        let response_payload = self
            .execute_foreign_chain_request(
                &foreign_tx_request.request,
                foreign_tx_request.payload_version,
            )
            .await?;

        let sign_request = build_signature_request(&foreign_tx_request, &response_payload)?;

        self.ecdsa_signature_provider
            .make_signature_follower_given_request(channel, presignature_id, sign_request)
            .await
```
