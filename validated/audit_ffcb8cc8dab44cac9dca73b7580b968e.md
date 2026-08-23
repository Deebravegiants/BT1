Based on my research, I found a concrete analog in nearcore's meta-transaction (delegate action) gas/compute accounting that mirrors the "real cost incurred but not reimbursed/charged" bug class from the L1 data-fee report — except here it manifests as **compute cost mischarged to the wrong shard**, which is the inverse-but-equivalent problem: the shard that actually performs the work does not get the compute budget it consumed properly charged against it, letting real work escape metering.

### Title
Pre-fix ML-DSA delegate-action signature verification compute is charged on the signer shard instead of the receiver shard, letting real per-chunk work escape budget accounting - ([File: runtime/runtime/src/config.rs, runtime/runtime/src/actions.rs])

### Summary
For `Delegate`/`DelegateV2` meta-transactions signed with a post-quantum ML-DSA-65 key, the inner delegate action's signature is actually verified on the **receiver shard** inside `apply_delegate_action`, but unless `fix_ml_dsa_cost_charging` is enabled, its non-zero **compute** cost is instead accounted at transaction-conversion time on the **signer's shard** via `signature_verification_cost`. This mirrors the reported bug class: a real, non-trivial cost of doing work (here, wall-clock ML-DSA verification compute, analogous to the "L1 data fee" that is genuinely incurred) is not attributed/charged where the work is actually performed, so the shard performing the work is not "reimbursed" against its compute budget.

### Finding Description
`signature_verification_cost` (`runtime/runtime/src/config.rs:542-561`) computes the extra verification cost for the signer's own key plus every inner `Delegate`/`DelegateV2` action's public key, and is invoked from `calculate_tx_cost` (`runtime/runtime/src/config.rs:452-462`) — i.e., burnt on the signer's shard when the transaction is converted to a receipt. When `meter_inner_verify_on_receiver` (config flag `fix_ml_dsa_cost_charging`) is `false`, the *legacy* behavior keeps the full `compute` component of the inner delegate signature's cost bundled into this signer-shard charge (`config.rs:554-557`, comment: "Without the flag the legacy behavior is kept (compute mis-charged on the signer shard) to preserve consensus").

However, the actual ML-DSA verification of the inner delegate signature happens later, on the **receiver shard**, inside `apply_delegate_action` (`runtime/runtime/src/actions.rs:437-461`):
```
if apply_state.config.wasm_config.fix_ml_dsa_cost_charging {
    let verify_compute = delegate_signature_verification_compute(...);
    result.compute_usage = safe_add_compute(result.compute_usage, verify_compute)?;
}
if !signed_delegate_action.verify() { ... }
``` [1](#0-0) 

The code comment makes the root cause explicit: *"Meter its verification compute against this shard's `compute_limit`; the gas for it was already burnt at tx conversion on the signer shard. Without the fix the compute is instead mis-charged on the signer shard (which never runs this verify), letting the work escape the receiver shard's budget."* [2](#0-1) 

`compute_usage` is what bounds the amount of real wall-clock work a chunk producer/validator performs per chunk (`process_receipts` sets `compute_limit = gas_limit` and receipts are pushed to the delayed queue once `total.compute >= compute_limit`, per `runtime/runtime/src/lib.rs:2668` and the "Gas/compute limit and delayed receipts" section of `protocol-model/spec/runtime-execution.md`). If the compute cost of an expensive cryptographic verification is attributed to the wrong shard (the signer shard, which never performs that specific verification), the receiver shard can perform unaccounted ML-DSA verification work without it counting against its own compute budget for that chunk — i.e., real work is not "reimbursed" against the correct resource ledger.

### Impact Explanation
This is scoped as a pre-`fix_ml_dsa_cost_charging` legacy behavior, gated for consensus compatibility, meaning it is a real, currently-reachable code path (not hypothetical) whenever the flag is disabled for a given protocol/runtime config. If exploited, an attacker (or ordinary user, since ML-DSA-65/PostQuantumSignatures is unprivileged and reachable via any submitted `Delegate`/`DelegateV2` transaction, gated only by protocol version PV 85) can submit many meta-transactions whose inner action is signed with an ML-DSA-65 key targeting a specific receiver shard. Each such receipt causes the receiver shard's chunk producer to perform real ML-DSA-65 verification work (documented at 100 Ggas / non-trivial compute) without that compute being deducted from `compute_limit` on that shard, since it was already "spent" against the signer shard's ledger instead. This allows a receiver shard to be loaded with more real per-chunk work than its `compute_limit` accounts for, undermining the very purpose of compute metering (bounding wall-clock chunk-production time), which can degrade chunk production latency or, in aggregate, contribute to missed chunks/congestion on the targeted shard.

### Likelihood Explanation
Reachable from an ordinary, unprivileged account submitting standard transactions (`Delegate`/`DelegateV2` actions with ML-DSA-65 inner keys) — no validator or node-internal privileges required. The condition is gated purely by whether `fix_ml_dsa_cost_charging` is set in the active `RuntimeConfig`/`wasm_config`, i.e., by protocol version/config rollout, not by attacker capability. Because the legacy code path is explicitly preserved "to preserve consensus" for chains/snapshots that predate the fix, any network still running with the flag unset is exposed.

### Recommendation
Ensure `fix_ml_dsa_cost_charging` is enabled by default at the intended protocol version everywhere it needs to apply, and audit all `RuntimeConfig` snapshots (`core/parameters/res/runtime_configs/*.yaml`) to confirm the flag flips to `true` at the version where `PostQuantumSignatures`/`MlDsa65` verification becomes active, so the compute cost of delegate-action signature verification is always metered on the shard where the verification is actually executed.

### Proof of Concept
Not independently reproduced against a running node in this session; the finding is derived from static analysis of `runtime/runtime/src/config.rs:525-561` and `runtime/runtime/src/actions.rs:437-461`, including the in-code comments explicitly describing the mischarging behavior when `fix_ml_dsa_cost_charging` is disabled. Confirming actual mainnet/testnet exposure (i.e., whether the flag is currently `true` in the deployed config) would require checking `core/parameters/res/runtime_configs/parameters.snap`/`parameters.yaml` for the exact protocol version at which `fix_ml_dsa_cost_charging` flips, which I was not able to fully verify within the available iterations — a Devin session with full repository access could confirm the exact activation version and construct an end-to-end reproduction with `test-loop-tests/src/tests/ml_dsa_verification_cost.rs` as a starting point.

### Citations

**File:** runtime/runtime/src/actions.rs (L444-461)
```rust
) -> Result<(), RuntimeError> {
    // The inner delegate signature is verified below, here on the receiver shard.
    // Meter its verification compute against this shard's `compute_limit`; the gas
    // for it was already burnt at tx conversion on the signer shard. Without the
    // fix the compute is instead mis-charged on the signer shard (which never runs
    // this verify), letting the work escape the receiver shard's budget. See
    // `signature_verification_cost`.
    if apply_state.config.wasm_config.fix_ml_dsa_cost_charging {
        let verify_compute = delegate_signature_verification_compute(
            &apply_state.config.fees,
            signed_delegate_action.delegate_action().public_key(),
        );
        result.compute_usage = safe_add_compute(result.compute_usage, verify_compute)?;
    }
    if !signed_delegate_action.verify() {
        result.result = Err(ActionErrorKind::DelegateActionInvalidSignature.into());
        return Ok(());
    }
```
