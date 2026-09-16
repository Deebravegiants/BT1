## Title
Relayer reward watermark not updated when reputation mint fails after treasury funds are already transferred, enabling repeated double-payment for the same block span - (File: `modules/pallets/consensus-incentives/src/impls.rs`)

### Summary
`Pallet::process_message` in `pallet-consensus-incentives` transfers the calculated block-cost reward from the treasury to the relayer, then attempts to mint a reputation-asset credit, and only afterwards updates `LastRewardedHeight` (the watermark used to compute the next reward's baseline). If the reputation mint step fails, the function returns an `Err` *before* the watermark update runs — even though the treasury-to-relayer currency transfer has already succeeded. This is structurally identical to the Malt `sellMalt()` finding: a real effect happens, but the accounting variable meant to track it is updated only after a later step that can short-circuit the function, so on failure the effect is recorded nowhere.

### Finding Description
In `process_message`:
```rust
T::Currency::transfer(&treasury, &relayer_account, reward, Preservation::Expendable)
    .map_err(|_| Error::<T>::RewardTransferFailed)?;

Self::deposit_event(Event::<T>::RelayerRewarded { ... });

T::ReputationAsset::mint_into(&relayer_account, reward.saturated_into())
    .map_err(|_| Error::<T>::ReputationMintFailed)?;

LastRewardedHeight::<T>::mutate(state_machine_id, |watermark| {
    *watermark = Some(watermark.unwrap_or_default().max(state_machine_height.height));
});
``` [1](#0-0) 

The order of operations is: (1) move funds out of the treasury, (2) emit the reward event, (3) mint reputation, (4) advance the watermark. Step 4 only runs if step 3 succeeds. But step 1 is irreversible by the time step 3 runs — the `?` on the mint call returns `Err(Error::<T>::ReputationMintFailed)` and the watermark mutation is skipped entirely.

The caller discards this error:
```rust
let _ = Self::process_message(
    state_machine_height,
    state_machine_id,
    relayer_account.clone().into(),
);
``` [2](#0-1) 

`calculate_reward` derives the reward for the *next* call using `LastRewardedHeight` as the baseline:
```rust
let baseline = LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height);
let blocks = latest_height.saturating_sub(baseline);
let reward = blocks_as_balance.saturating_mul(block_cost);
``` [3](#0-2) 

Because the watermark was never advanced after the failed mint, the *same* block span (`latest_height - baseline`) is recomputed and paid again on the very next consensus message for that state machine, and again on every subsequent failure — regardless of the reason `mint_into` failed (this is called for every `StateMachineUpdated` event batch, so it recurs naturally, unlike a one-off admin failure).

### Impact Explanation
This is an unbounded treasury drain: every time `T::ReputationAsset::mint_into` fails for a relayer/state-machine pair (e.g. reputation asset paused, frozen account, storage overflow, or any transient fungible-asset error), the treasury pays out the reward for that block span again on the next update, with no cap, because the watermark that prevents double-payment never advances. An attacker who can trigger repeated mint failures (or simply benefits from a naturally-occurring failure) can drain the treasury reward pool multiple times for blocks that were already compensated once — a direct loss of protocol funds analogous to the `totalProfit` miscount in the referenced report, where a real effect occurs but the compensating accounting write is skipped by an early exit.

### Likelihood Explanation
The transfer happens unconditionally as long as `reward` is non-zero, and the mint call is a genuinely separate fallible operation (a different pallet, `T::ReputationAsset`) that can fail for reasons unrelated to the relayer's honesty (e.g., asset paused, freeze, arithmetic overflow on `saturated_into()`). Because `on_executed` runs this path for every batch of `StateMachineUpdated` events and silently swallows the error (`let _ =`), any transient failure of the reputation mint reliably causes at least one repeated reward payment, and the condition can recur on every subsequent message until the mint succeeds — this is not a rare or attacker-privileged corner case.

### Recommendation
Move the `LastRewardedHeight::<T>::mutate` update to occur immediately after (or atomically with) the `T::Currency::transfer`, before the reputation mint, or make the reputation mint failure non-fatal (log and continue) rather than short-circuiting with `?`. Alternatively, wrap the whole reward-and-mint sequence in a single storage transaction (`frame_support::storage::with_transaction`) so that either both the transfer and the watermark update succeed together, or neither does — never leaving funds sent but the watermark unadvanced.

### Proof of Concept
1. Configure `pallet-consensus-incentives` with a non-zero `StateMachinesCostPerBlock` for some `state_machine_id`.
2. Arrange for `T::ReputationAsset::mint_into` to fail for the target relayer account (e.g., freeze/pause the reputation asset for that account, or use a mock in tests that returns `Err` — see the mint-failure mock pattern already used for `RewardTransferFailed` in `pallet_beefy_consensus_proofs.rs`'s "unpayable reward" test) [4](#0-3) .
3. Submit a consensus message causing a `StateMachineUpdated` event advancing `latest_height` for that state machine; `on_executed` calls `process_message`, which transfers the reward and then fails at `mint_into`, discarding the error via `let _ = ...` and never updating `LastRewardedHeight`.
4. Submit a second consensus message with the reputation mint now succeeding (or still failing) — `calculate_reward` computes the reward again using the same stale `baseline`, paying out the same block span from the treasury a second time, as shown by the existing rollback/re-payment test structure in `pallet_consensus_incentives.rs` [5](#0-4) .

### Citations

**File:** modules/pallets/consensus-incentives/src/impls.rs (L53-72)
```rust
			T::Currency::transfer(
				&T::TreasuryAccount::get().into_account_truncating(),
				&relayer_account,
				reward,
				Preservation::Expendable,
			)
			.map_err(|_| Error::<T>::RewardTransferFailed)?;

			Self::deposit_event(Event::<T>::RelayerRewarded {
				relayer: relayer_account.clone(),
				amount: reward,
				state_machine_height,
			});

			T::ReputationAsset::mint_into(&relayer_account, reward.saturated_into())
				.map_err(|_| Error::<T>::ReputationMintFailed)?;

			LastRewardedHeight::<T>::mutate(state_machine_id, |watermark| {
				*watermark = Some(watermark.unwrap_or_default().max(state_machine_height.height));
			});
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L92-97)
```rust
		let baseline = LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height);

		let blocks = latest_height.saturating_sub(baseline);

		let blocks_as_balance: <T as pallet_ismp::Config>::Balance = blocks.saturated_into();
		let reward = blocks_as_balance.saturating_mul(block_cost);
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L151-155)
```rust
				let _ = Self::process_message(
					state_machine_height,
					state_machine_id,
					relayer_account.clone().into(),
				);
```

**File:** modules/pallets/testsuite/src/tests/pallet_beefy_consensus_proofs.rs (L188-211)
```rust
/// Same hazard, different source: an unpayable reward. `pay_position_reward` runs after the
/// caller has applied the rotation, so propagating `RewardTransferFailed` rolls it back — and
/// since the mandatory justification is the only one obtainable for that session, every retry
/// fails identically until the treasury is topped up, leaving consensus on the old set. The
/// reward is the cheaper thing to drop. Messaging proofs deliberately keep the hard error.
#[test]
fn an_unpayable_reward_cannot_block_a_rotation() {
	let mut ext = new_test_ext();
	let height = 800u64;

	ext.execute_with(|| {
		// The BEEFY proofs treasury holds nothing in genesis, so any non-zero reward makes the
		// transfer fail with `RewardTransferFailed`.
		ProofReward::<Test>::put(1_000_000u128);

		pallet_beefy_consensus_proofs::Pallet::<Test>::settle_first_proof(
			submitter(11),
			vec![PROOF_TYPE_SP1, 0xab],
			Some(H256::repeat_byte(11)),
			PROOF_TYPE_SP1,
			Vec::new(),
			rotation_outcome(height, 30),
		)
		.expect("an unpayable reward must not reject the rotation");
```

**File:** modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs (L118-122)
```rust
// A relayer is paid once for advancing a state machine across a span of heights. When the latest
// height is rolled back and later resubmitted, the reward should still only cover the new blocks.
// The `LastRewardedHeight` watermark keeps each payout scoped to the span that has not been paid.
#[test]
fn reward_covers_only_unpaid_heights_after_rollback() {
```
