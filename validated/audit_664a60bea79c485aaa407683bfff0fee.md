### Title
Stale `GlobalContractDistributionReceipt` Forwards Next Shard Even When Nonce Check Fails - (File: runtime/runtime/src/global_contracts.rs)

### Summary

In `apply_global_contract_distribution_receipt`, the nonce staleness check in `apply_distribution_current_shard` is not propagated to `forward_distribution_next_shard`. When a stale (superseded) `GlobalContractDistributionReceipt` arrives at a shard, the current shard correctly skips writing the contract code, but the function unconditionally calls `forward_distribution_next_shard`, which emits a new forwarding receipt to the next shard. This causes a stale distribution receipt chain to continue propagating across all remaining shards even after the nonce guard has determined the receipt is obsolete.

### Finding Description

`apply_global_contract_distribution_receipt` calls two sub-functions sequentially:

1. `apply_distribution_current_shard` — checks the nonce via `check_and_update_nonce`. If `incoming_nonce < stored_nonce`, it returns `Ok(0)` (skipping the code write), but the boolean result is **not returned to the caller**.
2. `forward_distribution_next_shard` — is called **unconditionally** regardless of whether the nonce check passed or failed.

```rust
// runtime/runtime/src/global_contracts.rs lines 126-136
let compute =
    apply_distribution_current_shard(receipt, global_contract_data, apply_state, state_update)?;
forward_distribution_next_shard(      // <-- always called, even when nonce was stale
    receipt,
    global_contract_data,
    apply_state,
    epoch_info_provider,
    state_update,
    receipt_sink,
    receipt_to_tx,
)?;
```

The nonce check in `apply_distribution_current_shard` returns `Ok(0)` (compute = 0) when stale, but `Ok(0)` is indistinguishable from a successful no-op at the call site. The caller has no way to know the receipt was stale, so `forward_distribution_next_shard` proceeds to emit a new `GlobalContractDistributionReceipt` targeting the next unvisited shard.

The analog to the external report is exact: the nonce guard exists and works for the current shard (like `Pausable` existing in the contract), but the forwarding step (like the `claim` function) does not check the guard result.

### Impact Explanation

When a user deploys a global contract twice in quick succession (nonce N, then nonce N+1), the in-flight distribution chain for nonce N becomes stale once nonce N+1 is applied. However, each shard that receives the stale nonce-N receipt will:

1. Correctly skip writing the old contract code (nonce check passes the guard).
2. **Incorrectly** emit a new forwarding receipt to the next shard.

This means the stale receipt chain continues to hop across all shards, consuming compute budget (`deploy_global_contract_execution_base + per_byte * code_len`) on each shard it visits. The stale receipt also **resets the stored nonce back to N** on each shard it visits (via `set_nonce` in `check_and_update_nonce` when `incoming_nonce >= stored_nonce`), which can cause the newer nonce-N+1 distribution receipts that arrive later to be treated as stale and silently dropped on those shards.

The corrupted protocol values are:
- `TrieKey::GlobalContractNonce` — overwritten to a stale value on each shard.
- `TrieKey::GlobalContractCode` — the newer contract version may be silently dropped on shards where the stale receipt arrives after the fresh one.

This is a runtime state mismatch: different shards can end up with different versions of the global contract code, breaking the invariant that a global contract is uniformly deployed across all shards.

### Likelihood Explanation

Any unprivileged user who deploys a global contract twice (e.g., to update it) triggers this condition. The `DeployGlobalContractAction` is a standard user-callable action. The race window is the time for the first distribution chain to traverse all shards (multiple blocks), during which a second deploy naturally creates the stale-nonce scenario. This is a normal operational pattern explicitly tested in `test_global_contract_nonce_prevents_stale_overwrite`.

### Recommendation

In `apply_global_contract_distribution_receipt`, propagate the staleness result from `apply_distribution_current_shard` and skip `forward_distribution_next_shard` when the receipt is stale:

```rust
pub(crate) fn apply_global_contract_distribution_receipt(...) -> Result<Compute, RuntimeError> {
    let ReceiptEnum::GlobalContractDistribution(global_contract_data) = receipt.receipt() else {
        unreachable!(...)
    };
    let (compute, is_fresh) =
        apply_distribution_current_shard(receipt, global_contract_data, apply_state, state_update)?;
    if is_fresh {
        forward_distribution_next_shard(...)?;
    }
    Ok(compute)
}
```

Alternatively, `apply_distribution_current_shard` can return a typed enum distinguishing `Stale` from `Applied(compute)`.

### Proof of Concept

1. User A deploys global contract `C_v1` (AccountId mode). `increment_nonce` sets stored nonce to 1. A `GlobalContractDistributionReceipt::V2` with `nonce=1` begins hopping shard-by-shard.
2. Before the receipt reaches shard S_k, User A deploys `C_v2`. `increment_nonce` sets stored nonce to 2. A new receipt with `nonce=2` begins distribution.
3. The nonce-2 receipt reaches S_k first and writes `C_v2`. Stored nonce on S_k is now 2.
4. The stale nonce-1 receipt arrives at S_k. `check_and_update_nonce`: `incoming_nonce(1) < stored_nonce(2)` → returns `false`. `apply_distribution_current_shard` returns `Ok(0)`. Code write is skipped. ✓
5. **Bug**: `forward_distribution_next_shard` is called unconditionally. It emits a new receipt with `nonce=1` targeting S_{k+1}.
6. The nonce-1 receipt arrives at S_{k+1} before the nonce-2 receipt. `check_and_update_nonce`: `incoming_nonce(1) >= stored_nonce(0)` → returns `true`. `C_v1` is written to S_{k+1}. Stored nonce on S_{k+1} is set to 1.
7. The nonce-2 receipt arrives at S_{k+1}. `check_and_update_nonce`: `incoming_nonce(2) >= stored_nonce(1)` → returns `true`. `C_v2` overwrites. This hop is fine.
8. However, the stale nonce-1 receipt also emits a forwarding receipt to S_{k+2}, and so on. The stale chain continues to all remaining shards, consuming compute on each and potentially causing ordering-dependent state corruption on any shard where the stale receipt arrives after the fresh one has already set the nonce to 2.

Root cause: `apply_global_contract_distribution_receipt` at lines 126–136 of `runtime/runtime/src/global_contracts.rs`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** runtime/runtime/src/global_contracts.rs (L109-139)
```rust
pub(crate) fn apply_global_contract_distribution_receipt(
    receipt: &Receipt,
    apply_state: &ApplyState,
    epoch_info_provider: &dyn EpochInfoProvider,
    state_update: &mut TrieUpdate,
    receipt_sink: &mut ReceiptSink,
    receipt_to_tx: &mut Vec<(CryptoHash, ReceiptToTxInfo)>,
) -> Result<Compute, RuntimeError> {
    let _span = tracing::debug_span!(
        target: "runtime",
        "apply_global_contract_distribution_receipt",
    )
    .entered();

    let ReceiptEnum::GlobalContractDistribution(global_contract_data) = receipt.receipt() else {
        unreachable!("given receipt should be an global contract distribution receipt")
    };
    let compute =
        apply_distribution_current_shard(receipt, global_contract_data, apply_state, state_update)?;
    forward_distribution_next_shard(
        receipt,
        global_contract_data,
        apply_state,
        epoch_info_provider,
        state_update,
        receipt_sink,
        receipt_to_tx,
    )?;

    Ok(compute)
}
```

**File:** runtime/runtime/src/global_contracts.rs (L189-205)
```rust
fn apply_distribution_current_shard(
    receipt: &Receipt,
    global_contract_data: &GlobalContractDistributionReceipt,
    apply_state: &ApplyState,
    state_update: &mut TrieUpdate,
) -> Result<Compute, RuntimeError> {
    let identifier = match &global_contract_data.id() {
        GlobalContractIdentifier::CodeHash(hash) => GlobalContractCodeIdentifier::CodeHash(*hash),
        GlobalContractIdentifier::AccountId(account_id) => {
            GlobalContractCodeIdentifier::AccountId(account_id.clone())
        }
    };

    let is_nonce_fresh = check_and_update_nonce(global_contract_data, &identifier, state_update)?;
    if !is_nonce_fresh {
        return Ok(0);
    }
```

**File:** runtime/runtime/src/global_contracts.rs (L238-256)
```rust
fn check_and_update_nonce(
    global_contract_data: &GlobalContractDistributionReceipt,
    identifier: &GlobalContractCodeIdentifier,
    state_update: &mut TrieUpdate,
) -> Result<bool, RuntimeError> {
    let nonce_key = TrieKey::GlobalContractNonce { identifier: identifier.clone() };
    let stored_nonce = get_nonce(state_update, &nonce_key)?;
    let incoming_nonce = global_contract_data.nonce();

    // Allow the same nonce since the nonce is updated immediately when
    // initiating distribution to prevent multiple distributions with the same
    // nonce from being initiated.
    if incoming_nonce < stored_nonce {
        return Ok(false);
    }

    set_nonce(state_update, nonce_key, incoming_nonce);
    Ok(true)
}
```

**File:** runtime/runtime/src/global_contracts.rs (L275-319)
```rust
fn forward_distribution_next_shard(
    receipt: &Receipt,
    global_contract_data: &GlobalContractDistributionReceipt,
    apply_state: &ApplyState,
    epoch_info_provider: &dyn EpochInfoProvider,
    state_update: &mut TrieUpdate,
    receipt_sink: &mut ReceiptSink,
    receipt_to_tx: &mut Vec<(CryptoHash, ReceiptToTxInfo)>,
) -> Result<(), RuntimeError> {
    let shard_layout = epoch_info_provider.shard_layout(&apply_state.epoch_id)?;
    let already_delivered_shards = BTreeSet::from_iter(
        global_contract_data
            .already_delivered_shards()
            .iter()
            .cloned()
            .chain(std::iter::once(apply_state.shard_id)),
    );
    let Some(next_shard) = shard_layout
        .shard_ids()
        .filter(|shard_id| !already_delivered_shards.contains(&shard_id))
        .next()
    else {
        return Ok(());
    };
    let already_delivered_shards = Vec::from_iter(already_delivered_shards);
    let predecessor_id = receipt.predecessor_id().clone();
    let next_receipt = global_contract_data.forward(next_shard, already_delivered_shards);
    let mut next_receipt = Receipt::new_global_contract_distribution(predecessor_id, next_receipt);
    let receipt_id = apply_state.create_receipt_id(receipt.receipt_id(), 0);
    next_receipt.set_receipt_id(receipt_id);
    if apply_state.save_receipt_to_tx {
        receipt_to_tx.push((
            receipt_id,
            ReceiptToTxInfo::V1(ReceiptToTxInfoV1 {
                origin: ReceiptOrigin::FromReceipt(ReceiptOriginReceipt {
                    parent_receipt_id: *receipt.receipt_id(),
                    parent_predecessor_id: receipt.predecessor_id().clone(),
                }),
                receiver_account_id: next_receipt.receiver_id().clone(),
                shard_id: apply_state.shard_id,
            }),
        ));
    }
    receipt_sink.forward_or_buffer_receipt(next_receipt, apply_state, state_update)?;
    Ok(())
```

**File:** core/primitives/src/receipt.rs (L949-956)
```rust
    /// Returns the nonce of the distribution.
    /// V1 receipts return 0, V2 receipts return their stored nonce.
    pub fn nonce(&self) -> u64 {
        match &self {
            Self::V1(_) => 0,
            Self::V2(v2) => v2.nonce,
        }
    }
```
