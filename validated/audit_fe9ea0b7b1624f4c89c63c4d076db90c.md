The code is confirmed. Let me trace the exact logic and check whether the on-chain `quorum` field is ever enforced at the node level.

**Key facts from the code:**

**1. `FanOut::extract` silently discards transient errors and accepts a single success** [1](#0-0) 

When N-1 inspectors return transient errors, they are stored only in `first_transient_error` (discarded from quorum counting). The `successes` vec ends up with 1 element. [2](#0-1) 

`all_successes_agree` over a 1-element vec is trivially `true`, so `Ok(first)` is returned unconditionally.

**2. `NotFinalized` is classified as transient** [3](#0-2) 

`NotFinalized`, `ClientError`, and `RpcRequestFailed` are all transient. `NotFinalized` is a *natural* state — no network-level DoS is needed to produce it; it occurs organically during the finality window.

**3. The on-chain `ChainEntry.quorum` field exists and is validated at the contract level** [4](#0-3) [5](#0-4) 

The contract enforces `quorum > 0` and `quorum <= providers_len`. However, `FanOut` has no `quorum` parameter and never reads this value.

**4. The whitelist verifier is advisory-only (log-only)** [6](#0-5) 

It emits diagnostics but does not block signing or enforce quorum at runtime.

---

**Assessment against reject criteria:**

- *"Requires network-level DoS"*: The `NotFinalized` path requires **no DoS**. During the finality window, N-1 honest RPCs naturally return `NotFinalized` (transient). The attacker only needs to control one provider and time the request during this window.
- *"External dependency behavior is the only cause"*: No — the root cause is the **missing quorum enforcement** in `FanOut::extract`. The on-chain quorum is defined but never consulted by the node.
- *"Trusted operator access"*: Compromising a third-party RPC provider (e.g., Alchemy, Infura) is not "trusted operator access." The entire purpose of multi-provider `FanOut` is to protect against exactly this.
- *"Liveness slowdown only"*: No — this is a security bypass enabling a forged foreign-chain observation to be signed.

---

### Title
FanOut::extract Accepts Single-Provider Success When N-1 Providers Return Transient Errors, Bypassing On-Chain RPC Quorum — (`crates/foreign-chain-inspector/src/lib.rs`)

### Summary
`FanOut::extract` silently discards transient errors (including `NotFinalized`, which occurs naturally during the finality window) and accepts a single `Ok` result as authoritative. The on-chain `ChainEntry.quorum` field is defined and validated at the contract level but is never read or enforced by the node's `FanOut` logic. An attacker who controls one configured RPC provider can exploit the natural `NotFinalized` window to inject attacker-controlled foreign-chain observations that the MPC network will sign.

### Finding Description
In `FanOut::extract` (`lib.rs:92–141`), results from N concurrent inspector tasks are partitioned into `successes`, `non_transient_errors`, and `first_transient_error`. Transient errors — including `NotFinalized` (line 272), `ClientError` (line 269), and `RpcRequestFailed` (line 270) — are silently dropped from quorum accounting. [7](#0-6) 

When N-1 providers return `NotFinalized` (a natural state during the finality window) and 1 provider returns `Ok(attacker_values)`, the `successes` vec contains exactly one element. The `all_successes_agree` check at line 131 is trivially satisfied over a single-element vec, and `Ok(attacker_values)` is returned. [2](#0-1) 

The on-chain `ChainEntry.quorum` field — which specifies the minimum number of providers that must agree — is validated at the contract level: [5](#0-4) 

But `FanOut` has no quorum parameter and never consults this value. The whitelist verifier is log-only and does not enforce quorum at signing time. [6](#0-5) 

### Impact Explanation
An attacker who controls one configured RPC provider can cause the MPC network to issue a threshold signature over attacker-controlled foreign-chain observations (e.g., fabricated transaction amounts, recipients, or token types). This directly enables unauthorized threshold signature issuance and forged foreign-chain verification, matching the Critical and High impact scopes.

### Likelihood Explanation
The `NotFinalized` transient state occurs naturally during the finality window of every foreign-chain transaction — no network-level DoS is required. The attacker only needs to:
1. Control one of the RPC providers configured by a node operator (e.g., by compromising a third-party RPC service, or by being a malicious provider that was whitelisted via threshold vote).
2. Time the signing request during the finality window when N-1 honest providers legitimately return `NotFinalized`.

This is a realistic attack window for any bridge transaction.

### Recommendation
Enforce the on-chain `quorum` value inside `FanOut::extract`. Before returning a success, verify that `successes.len() >= quorum`. If fewer than `quorum` providers returned a non-transient success, return a new error variant (e.g., `InsufficientQuorum { got: usize, required: u64 }`) rather than accepting the partial result. The `quorum` value must be threaded from `ChainEntry` into the `FanOut` constructor or passed as a parameter to `extract`.

### Proof of Concept
```rust
// Pseudocode integration test
let attacker_values = vec![fake_extracted_value()];
let inspectors: Vec<MockInspector> = vec![
    MockInspector::returning(Err(ForeignChainInspectionError::NotFinalized)), // honest, transient
    MockInspector::returning(Err(ForeignChainInspectionError::NotFinalized)), // honest, transient
    MockInspector::returning(Ok(attacker_values.clone())),                    // attacker-controlled
];
let fanout = FanOut::new(NonEmptyVec::try_from(inspectors).unwrap());
let result = fanout.extract(tx_id, finality, extractors).await;
// Asserts Ok(attacker_values) — single attacker success accepted, quorum bypassed
assert_eq!(result.unwrap(), attacker_values);
```

This test (matching the structure of `crates/foreign-chain-inspector/tests/fanout.rs`) would pass against the current code, confirming the quorum bypass. [8](#0-7)

### Citations

**File:** crates/foreign-chain-inspector/src/lib.rs (L37-57)
```rust
/// Combines multiple inspectors that target the same chain into a single inspector.
///
/// All inner inspectors are queried concurrently. The fan-out treats every
/// non-transient outcome (success or non-transient error, see
/// [`ForeignChainInspectionError::is_transient`]) as a substantive verdict that must
/// agree across inspectors. Transient errors (network issues, finality not yet reached,
/// etc.) are tolerated so that a single unavailable RPC does not take the whole node
/// out of signing.
///
/// Outcomes:
/// * All substantive verdicts are `Ok` with the same extracted values → returns those values.
/// * All substantive verdicts are non-transient errors of the same variant → returns one of
///   them (e.g. all inspectors agree the transaction failed).
/// * Substantive verdicts disagree (`Ok` vs. non-transient error, two different non-transient
///   error variants, or two different success values) → returns
///   [`ForeignChainInspectionError::InspectorResponseMismatch`].
/// * Every inspector returned a transient error → the first such error is propagated.
///
/// Variant-level comparison is used for non-transient errors, so inspectors that all report
/// the same failure mode (e.g. `NonCanonicalBlock`) are considered to agree even if the
/// inner fields differ.
```

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

**File:** crates/foreign-chain-inspector/src/lib.rs (L130-141)
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
```

**File:** crates/foreign-chain-inspector/src/lib.rs (L266-275)
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
}
```

**File:** crates/contract/src/foreign_chain_rpc.rs (L45-48)
```rust
pub struct ChainEntry {
    providers: NonEmptyBTreeMap<ProviderId, ProviderConfig>,
    quorum: u64,
}
```

**File:** crates/contract/src/foreign_chain_rpc.rs (L55-69)
```rust
        if quorum == 0 {
            return Err(ChainEntryValidationError::ZeroQuorum);
        }
        let providers_len = u64::try_from(providers.len()).map_err(|e| {
            ChainEntryValidationError::ProvidersLenOverflow {
                len: providers.len(),
                reason: e.to_string(),
            }
        })?;
        if quorum > providers_len {
            return Err(ChainEntryValidationError::QuorumExceedsProviders {
                quorum,
                providers_len,
            });
        }
```

**File:** crates/node/src/foreign_chain_whitelist_verifier.rs (L1-7)
```rust
//! Log-only check that the node's local foreign-chain RPC config matches the
//! on-chain whitelist (`allowed_foreign_chain_providers`).
//!
//! On a fresh deployment with an unvoted whitelist, the verifier emits one
//! `ChainNotInWhitelist` info per configured chain — expected during rollout,
//! clears once the whitelist is populated and the watch channel updates.

```
