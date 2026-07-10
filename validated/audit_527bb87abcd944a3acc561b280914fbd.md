### Title
Non-Deterministic JSON String in `AptosEvent.data` Causes Inter-Node `ForeignTxSignPayload` Hash Divergence, Permanently Freezing Bridge Funds - (File: crates/near-mpc-contract-interface/src/types/foreign_chain.rs)

---

### Summary

The `AptosEvent.data` field is a raw `String` populated directly from the Aptos RPC JSON response. Because JSON object key ordering is not guaranteed across different RPC providers, different MPC nodes independently querying different providers for the same Aptos transaction may receive semantically identical event data serialized with different key orderings. Each node Borsh-serializes its own `AptosEvent` into `ForeignTxSignPayload` and hashes it; divergent raw strings produce divergent hashes. The signing threshold is never reached, and the pending `verify_foreign_transaction` request times out — permanently freezing the user's bridge funds that are locked on the Aptos side awaiting the MPC attestation.

---

### Finding Description

**Root cause — raw JSON string stored without normalization**

`AptosEvent` is defined in `crates/near-mpc-contract-interface/src/types/foreign_chain.rs`. Its `data` field is a plain `String`:

```rust
pub struct AptosEvent {
    pub account_address: AptosAddress,
    pub sequence_number: u64,
    pub type_tag: String,
    pub data: String,   // raw JSON string from Aptos RPC
}
```

The test at line 1929 confirms the field carries a raw JSON literal:

```rust
data: "{\"amount\":\"100\"}".to_string(),
```

**Hash computation path**

`ForeignTxSignPayload::compute_msg_hash` (lines 1504–1509) Borsh-serializes the entire payload — including the `AptosEvent.data` string byte-for-byte — and SHA-256 hashes it:

```rust
impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
}
```

Borsh serializes a `String` as its UTF-8 bytes prefixed by a 4-byte length. Two strings `{"amount":"100","recipient":"0xAA"}` and `{"recipient":"0xAA","amount":"100"}` are semantically identical JSON but produce different byte sequences, and therefore different SHA-256 hashes.

**Node-side execution path**

In `crates/node/src/providers/verify_foreign_tx/sign.rs`, both the leader (lines 73–86) and every follower (lines 103–114) independently call `execute_foreign_chain_request`, which queries the Aptos RPC and builds the `ForeignTxSignPayload`. Each node uses a deterministically selected but **distinct** RPC provider (per the provider-selection design). The resulting `sign_request` payload hash is fed directly into the ECDSA signing protocol:

```rust
let sign_request = build_signature_request(&foreign_tx_request, &response_payload)?;
```

If any node's `response_payload` differs in the `data` string, its `sign_request.payload` hash differs, and the partial signatures it produces are for a different message — they will never combine with the other nodes' shares to form a valid threshold signature.

**Attacker-controlled entry path**

An unprivileged user calls `verify_foreign_transaction` on the NEAR contract referencing any Aptos transaction whose event data is a JSON object with two or more keys (the common case for any non-trivial bridge event). No privileged access is required: the user only needs to submit a valid `VerifyForeignTransactionRequestArgs`. The divergence is triggered by the whitelisted RPC providers returning the same Move-struct event data serialized with different JSON key orderings — a routine behavior difference between providers using different JSON libraries (e.g., Go's `encoding/json` sorts keys alphabetically, while some Node.js or Python implementations preserve insertion order).

---

### Impact Explanation

**Critical — permanent freezing of funds in the verified foreign-chain flow.**

The Omnibridge inbound flow locks user funds on the Aptos side and waits for the MPC network to attest the transaction before releasing them on NEAR. If the `verify_foreign_transaction` request permanently fails to reach threshold (because nodes compute divergent hashes), the locked funds cannot be released. The request times out with no on-chain failure response (per the known limitation documented in the design), and the user has no recourse: retrying produces the same divergence as long as the RPC providers return different orderings. The funds are permanently frozen in the bridge contract.

---

### Likelihood Explanation

**High.** Aptos event data is a Move struct serialized to JSON by the RPC node. The JSON key ordering is an implementation detail of each provider's serialization library. The MPC network is designed to use multiple whitelisted providers (e.g., Alchemy, Infura, self-hosted nodes), each potentially using a different JSON serialization stack. Any Aptos event with two or more fields — which covers all realistic bridge events — is susceptible. No attacker action is required beyond submitting a normal bridge request; the divergence occurs naturally under the multi-provider architecture.

---

### Recommendation

Normalize the Aptos event `data` JSON string to a canonical form before storing it in `AptosEvent`. The standard approach is to parse the raw JSON into a value tree and re-serialize it with lexicographically sorted keys. This must be done inside the Aptos inspector, before the `AptosEvent` is constructed, so that all nodes produce the same byte sequence regardless of which provider they queried.

```rust
// In the Aptos inspector, before constructing AptosEvent:
let canonical_data = canonicalize_json(&raw_data_string)?;
// where canonicalize_json parses and re-serializes with sorted keys
```

Alternatively, define `data` as a structured Borsh-serializable type (a `BTreeMap<String, AptosValue>`) rather than a raw string, so the canonical ordering is enforced by the type system.

The design document already states: *"Extractors must be deterministic and specified independently of provider-specific JSON formatting"* — this fix brings the implementation into compliance with that stated invariant.

---

### Proof of Concept

1. Deploy an Aptos Move module that emits an event with two fields, e.g. `{ "amount": "1000000", "recipient": "0xdeadbeef" }`.
2. Execute a transaction that triggers the event and lock funds in the Omnibridge contract.
3. Submit `verify_foreign_transaction` on NEAR referencing that transaction, targeting the `ForeignTx` domain.
4. Observe that Node A (using Provider P1, which returns `{"amount":"1000000","recipient":"0xdeadbeef"}`) computes hash H1, while Node B (using Provider P2, which returns `{"recipient":"0xdeadbeef","amount":"1000000"}`) computes hash H2 ≠ H1.
5. The ECDSA signing protocol receives partial signatures for two different messages; aggregation fails; the request times out.
6. The user's funds remain locked in the Aptos bridge contract with no release path.

The divergence can be reproduced locally by constructing two `AptosEvent` values with the same semantic data but different `data` string orderings and verifying that `compute_msg_hash` returns different values — which follows directly from the Borsh string serialization being byte-exact.