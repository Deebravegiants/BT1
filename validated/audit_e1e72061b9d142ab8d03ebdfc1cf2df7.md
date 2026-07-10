### Title
Single Compromised RPC Provider Can Forge Foreign-Chain Verification Result — (`File: crates/foreign-chain-inspector/src/lib.rs`)

---

### Summary

The `FanOut<Inspector>` implementation that aggregates results from multiple RPC providers accepts a **single provider's success** as the verified truth whenever all other providers return transient errors. There is no minimum quorum enforcement. A single compromised or malicious whitelisted RPC provider can therefore fabricate a foreign-chain verification result that the MPC network will sign, enabling invalid bridge execution.

---

### Finding Description

`FanOut<Inspector>` in `crates/foreign-chain-inspector/src/lib.rs` queries all configured inspectors concurrently and classifies each outcome as a success, a non-transient error, or a transient error. [1](#0-0) 

After collecting all outcomes, the aggregation logic checks only that **all successes agree with each other** — it does not enforce a minimum count of agreeing successes: [2](#0-1) 

If exactly **one** provider returns `Ok(values)` and every other provider returns a transient error (e.g., `NotFinalized`, `RpcRequestFailed`, `ClientError`), the condition `all_successes_agree` is trivially satisfied over a one-element list, and the single provider's fabricated result is returned as the verified truth.

The design documentation explicitly acknowledges that quorum enforcement is **not yet implemented**: [3](#0-2) 

The `is_transient()` predicate classifies `NotFinalized` and `NotEnoughBlockConfirmations` as transient: [4](#0-3) 

These are natural, non-adversarial states that real providers legitimately return during the window between transaction submission and finality — no denial-of-service is required to produce them.

---

### Impact Explanation

Each MPC node independently calls `execute_foreign_chain_request`, which calls the inspector (potentially a `FanOut`) and uses the returned `ForeignTxSignPayload` as the message to sign: [5](#0-4) 

If a compromised provider causes `FanOut` to return fabricated extracted values, the node computes a `msg_hash` over those values and contributes a signature share. If a signing-threshold number of nodes are each misled (each having the compromised provider as their only non-transient responder during the attack window), the MPC network produces a valid threshold signature over a forged observation. The design documentation acknowledges this directly: [6](#0-5) 

The resulting signature is indistinguishable from a legitimate one and can be used to claim bridge funds for a transaction that never finalized or never occurred, constituting **forged foreign-chain verification enabling invalid bridge execution or double-spend**.

---

### Likelihood Explanation

The attack requires:

1. **One compromised whitelisted RPC provider** — below any signing threshold; no collusion among MPC participants is needed.
2. **A natural transient-error window** — real providers legitimately return `NotFinalized` between transaction submission and finality. No DoS is required; the attacker simply submits the `verify_foreign_transaction` request during this window.
3. **The compromised provider to be selected by ≥ signing-threshold nodes** — with deterministic provider selection (`sha256(participant_id || request_id || provider_rpc_url)`), the attacker can predict which nodes will query which provider and time the request accordingly.

RPC provider compromises are realistic (BGP hijacks, API key theft, supply-chain attacks on provider infrastructure). The attack window (the finality gap) exists for every transaction on every supported chain.

---

### Recommendation

Enforce the on-chain `ChainEntry.quorum` value inside `FanOut::extract()`. Before returning a success, assert that `successes.len() >= quorum`. If fewer than `quorum` providers agree, return `ForeignChainInspectionError::InspectorResponseMismatch` rather than accepting the minority result. This matches the stated design requirement: [7](#0-6) 

Until the quorum value is available at the `FanOut` call site, a safe interim measure is to require **all** non-transient outcomes to be successes (i.e., reject if any provider returns a transient error while another returns success), which is stricter than the current logic.

---

### Proof of Concept

**Setup**: A chain (e.g., Polygon) is configured with 3 whitelisted providers: `P1` (compromised), `P2`, `P3`. The on-chain `quorum = 2`.

**Attack**:

1. Attacker submits `verify_foreign_transaction` for a real transaction `T` that has been broadcast but not yet finalized on Polygon.
2. `P2` and `P3` return `ForeignChainInspectionError::NotFinalized` (transient — classified by `is_transient()` at line 266–274 of `lib.rs`).
3. `P1` (compromised) returns `Ok(vec![ExtractedValue::BlockHash(attacker_chosen_hash)])` — a fabricated block hash.
4. Inside `FanOut::extract()` (lines 130–141 of `lib.rs`): `successes = [(0, [attacker_hash])]`, `non_transient_errors = []`, `first_transient_error = Some(NotFinalized)`. The check `all_successes_agree` passes trivially (one element). `Ok([attacker_hash])` is returned.
5. Each MPC node that has `P1` as its only non-transient responder computes `msg_hash = SHA-256(borsh(ForeignTxSignPayload { request, values: [attacker_hash] }))` and contributes a signature share.
6. If ≥ signing-threshold nodes are in this state simultaneously, the MPC network produces a valid ECDSA signature over the forged payload.
7. Attacker presents the signature on NEAR to claim bridge funds corresponding to a transaction that was never finalized (or was later reverted).

The root cause — absence of quorum enforcement in `FanOut::extract()` — is at: [8](#0-7)

### Citations

**File:** crates/foreign-chain-inspector/src/lib.rs (L92-116)
```rust
        let mut successes: Vec<(usize, Vec<Self::ExtractedValue>)> = Vec::new();
        let mut non_transient_errors: Vec<(usize, ForeignChainInspectionError)> = Vec::new();
        let mut first_transient_error: Option<ForeignChainInspectionError> = None;

        for (idx, result) in join_set.join_all().await {
            match result {
                Ok(values) => successes.push((idx, values)),
                Err(err) if err.is_transient() => {
                    tracing::warn!(
                        inspector_index = idx,
                        error = %err,
                        "fan-out inspector failed (transient)",
                    );
                    first_transient_error.get_or_insert(err);
                }
                Err(err) => {
                    tracing::error!(
                        inspector_index = idx,
                        error = %err,
                        "fan-out inspector failed (non-transient)",
                    );
                    non_transient_errors.push((idx, err));
                }
            }
        }
```

**File:** crates/foreign-chain-inspector/src/lib.rs (L130-142)
```rust
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

**File:** crates/foreign-chain-inspector/src/lib.rs (L265-275)
```rust
impl ForeignChainInspectionError {
    pub fn is_transient(&self) -> bool {
        matches!(
            self,
            Self::ClientError(_)
                | Self::RpcRequestFailed(_)
                | Self::NotFinalized
                | Self::NotEnoughBlockConfirmations { .. }
        )
    }
}
```

**File:** docs/design/allowing-per-node-foreign-chain-rpc-configuration.md (L27-27)
```markdown
4. Every node partaking in a foreign signature verification request queries all its locally configured RPC providers for the relevant chain, independently of other nodes. A quorum of those RPC providers must agree on the verification; if fewer than the quorum agree, the node errors out that foreign-tx validation and does **not** retry the request.
```

**File:** docs/design/allowing-per-node-foreign-chain-rpc-configuration.md (L119-122)
```markdown
### Individual node quorum of RPC providers for verification requests

When a foreign TX verification request is processed by a set of nodes, every node individually queries its locally-configured RPC providers for that chain. A node considers the foreign TX verified iff at least the per-chain RPC quorum of providers agreed. If fewer than the RPC quorum agree, the node errors out and produces no signature share. This sub-quorum outcome must be **terminal** for the request — the leader does not re-attempt it. This is an implementation requirement, not current behavior. See [Calculating the whitelisted and available foreign-chain sets](calculating-supported-foreign-chains.md#verification-behavior).

```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L73-86)
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
```

**File:** docs/foreign-chain-transactions.md (L652-656)
```markdown
* **RPC trust and correctness**: Verification relies on centralized RPC providers. A malicious
  or faulty provider could return incorrect data for a subset of nodes.
* **No additional consensus**: Nodes independently query providers and do not participate on failures.
  If a threshold of nodes are misled by providers, the network could sign invalid observations.
* **Provider availability**: Outages or rate limits can cause verification failures and reduced
```
