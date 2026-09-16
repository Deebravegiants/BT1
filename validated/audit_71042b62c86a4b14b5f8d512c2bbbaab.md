Found a strong analog: `StreamingYieldVault.sol`'s `_lockedYield()` computes linear vesting based on `_vestingStart`, and `_startVesting()` resets `_vestingStart = block.timestamp` on every `addYield` call — but only after asserting the previous tranche fully vested (`block.timestamp >= start + VEST`) and the deposit window has passed. This guard means a new tranche can only start once the old one is *fully* unlocked (elapsed == VEST, so `_lockedYield()` was already 0), so there is no mid-vest reset that would strand or re-lock already-vested value the way the Volt oracle's `startTime` reset did mid-accrual.

### Title
No vulnerability found for this question - ([File: N/A])

### Summary
The C4 report describes Volt's `ScalingPriceOracle` resetting `startTime` (and therefore the accrual baseline) in `requestCPIData()` while `oraclePrice` is only updated later in `fulfill()`, so triggering a new request before fulfillment collapses `getCurrentOraclePrice()` back toward the stale `oraclePrice` and discards the interpolated gains — an unprivileged party can trigger this reset at will.

### Finding Description
I searched Hyperbridge broadly for the same bug shape: a stored baseline (`startTime`/`lastUpdate`/`_vestingStart`/reward "previous height") used to interpolate or compound a value over time, that gets reset by an unprivileged, re-triggerable action *before* the dependent value is durably applied, causing loss of already-accrued value. Candidates examined:

- `VWAPOracle.sol` (`_updateCumulativeSpread`) — cumulative weighted-average, not time-interpolated; `lastUpdate` is stored but never used to compute a value, so no reset-before-compound issue. [1](#0-0) 
- `pallet-consensus-incentives` `calculate_reward`/`process_message` — this pallet explicitly documents and fixes the exact bug class (baseline could be re-read multiple times per batch, and rollback could double-pay); it now uses a monotonic `LastRewardedHeight` watermark that only advances forward, with a regression test proving rollback-then-resubmit only pays for the net new span. [2](#0-1) [3](#0-2) 
- `beefy-consensus-proofs::verify_and_apply` — uses `LastRewardedDispatchRoot` and `prev_height`/`latest_height` comparisons with explicit anti-replay/anti-restart checks (`NoNewWork`, `StaleProof`), and comments document prior fixes to prevent stale/duplicate reward paths. [4](#0-3) 
- `StreamingYieldVault.sol` `_startVesting`/`_lockedYield` — the closest structural analog (a time-baseline reset that drives a linear-interpolation "unlocked value" function), but `_startVesting` reverts unless the current tranche has already fully vested (`block.timestamp >= start + VEST`) and the deposit window has elapsed, so `_vestingStart` can never be reset while `_lockedYield()` is still nonzero. [5](#0-4) 
- `ismp::core::handlers::consensus::update_client` — `latest_commitment_height`/`previous_latest_height` are read from host storage and only advance monotonically per state machine per verified proof; there is no mid-accrual "start" reset reachable by an unprivileged relayer that would discard already-verified commitments. [6](#0-5) 

None of these reachable, unprivileged-triggerable paths reproduce Volt's failure mode of "an unprivileged actor resets the accrual baseline before the dependent value is durably committed, discarding already-accrued value." The closest analog (`StreamingYieldVault`) is explicitly guarded against exactly this scenario, and the consensus-reward pallets already carry watermark/anti-replay fixes with regression tests targeting this precise bug class.

### Impact Explanation
N/A — no exploitable analog found.

### Likelihood Explanation
N/A — no exploitable analog found.

### Recommendation
N/A.

### Proof of Concept
N/A.

### Citations

**File:** evm/src/utils/VWAPOracle.sol (L276-281)
```text
    function _updateCumulativeSpread(CumulativeSpreadData storage data, int256 weightedSpread, uint256 volume) private {
        data.weightedSpreadSum += weightedSpread;
        data.totalVolume += volume;
        data.fillCount += 1;
        data.lastUpdate = block.timestamp;
    }
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L70-99)
```rust
			LastRewardedHeight::<T>::mutate(state_machine_id, |watermark| {
				*watermark = Some(watermark.unwrap_or_default().max(state_machine_height.height));
			});
		}
		Ok(())
	}

	/// Calculate the reward for a message based on the state machine id
	fn calculate_reward(
		state_machine_id: &StateMachineId,
		block_cost: <T as pallet_ismp::Config>::Balance,
	) -> Result<<T as pallet_ismp::Config>::Balance, Error<T>> {
		let host = <T::IsmpHost>::default();
		let latest_height = host
			.latest_commitment_height(state_machine_id.clone())
			.map_err(|_| Error::<T>::CouldNotGetStateMachineHeight)?;
		let previous_height =
			host.previous_commitment_height(state_machine_id.clone()).unwrap_or_default();

		// Use the rewarded watermark as the baseline and fall back to the previous height until
		// the first reward is recorded for this chain. The watermark only moves forward, so a
		// height that is rolled back and later resubmitted is not paid for a second time.
		let baseline = LastRewardedHeight::<T>::get(state_machine_id).unwrap_or(previous_height);

		let blocks = latest_height.saturating_sub(baseline);

		let blocks_as_balance: <T as pallet_ismp::Config>::Balance = blocks.saturated_into();
		let reward = blocks_as_balance.saturating_mul(block_cost);

		Ok(reward)
```

**File:** modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs (L118-219)
```rust
// A relayer is paid once for advancing a state machine across a span of heights. When the latest
// height is rolled back and later resubmitted, the reward should still only cover the new blocks.
// The `LastRewardedHeight` watermark keeps each payout scoped to the span that has not been paid.
#[test]
fn reward_covers_only_unpaid_heights_after_rollback() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		const BLOCK_COST: u128 = 100;
		let host = Ismp::default();
		let state_machine_id = setup_state_machine();
		let treasury_account: AccountId32 = PalletId(*b"treasury").into_account_truncating();

		pallet_consensus_incentives::Pallet::<Test>::update_cost_per_block(
			RuntimeOrigin::root(),
			state_machine_id,
			BLOCK_COST,
		)
		.unwrap();

		let (consensus_message, relayer_account) = setup_host_and_message(&host);
		let message = MessageWithWeight { message: consensus_message, weight: Weight::zero() };
		let updated = |height: u64| {
			vec![IsmpEvent::StateMachineUpdated(StateMachineUpdated {
				state_machine_id,
				latest_height: height,
			})]
		};

		// The chain has already advanced to 1025 and every block up to it has been rewarded once.
		host.store_state_machine_commitment(
			StateMachineHeight { id: state_machine_id, height: 1024 },
			commitment(),
		)
		.unwrap();
		host.store_latest_commitment_height(StateMachineHeight {
			id: state_machine_id,
			height: 1024,
		})
		.unwrap();
		host.store_state_machine_commitment(
			StateMachineHeight { id: state_machine_id, height: 1025 },
			commitment(),
		)
		.unwrap();
		host.store_latest_commitment_height(StateMachineHeight {
			id: state_machine_id,
			height: 1025,
		})
		.unwrap();

		let treasury_before_first = Balances::balance(&treasury_account);
		<pallet_consensus_incentives::Pallet<Test> as FeeHandler>::on_executed(
			vec![message.clone()],
			updated(1025),
		)
		.unwrap();

		assert_eq!(Balances::balance(&treasury_account), treasury_before_first - BLOCK_COST);
		assert_eq!(
			pallet_consensus_incentives::LastRewardedHeight::<Test>::get(state_machine_id),
			Some(1025)
		);

		// The previous-height pointer references an older height whose commitment is no longer
		// retained in the bounded map.
		pallet_ismp::PreviousStateMachineHeight::<Test>::insert(state_machine_id, 1);

		// Deleting the latest commitment rolls the latest height back to that previous pointer.
		host.delete_state_commitment(StateMachineHeight { id: state_machine_id, height: 1025 })
			.unwrap();
		assert_eq!(host.latest_commitment_height(state_machine_id).unwrap(), 1);

		// The next honest consensus update advances to 1030, carrying the stale pointer forward as
		// the new previous height.
		host.store_state_machine_commitment(
			StateMachineHeight { id: state_machine_id, height: 1030 },
			commitment(),
		)
		.unwrap();
		host.store_latest_commitment_height(StateMachineHeight {
			id: state_machine_id,
			height: 1030,
		})
		.unwrap();
		assert_eq!(host.previous_commitment_height(state_machine_id), Some(1));

		let treasury_before_second = Balances::balance(&treasury_account);
		<pallet_consensus_incentives::Pallet<Test> as FeeHandler>::on_executed(
			vec![message],
			updated(1030),
		)
		.unwrap();

		// The real advance is 1025 -> 1030, so only the 5 new blocks are paid rather than the full
		// span back to the previous pointer.
		assert_eq!(Balances::balance(&treasury_account), treasury_before_second - 5 * BLOCK_COST);
		assert_eq!(
			pallet_consensus_incentives::LastRewardedHeight::<Test>::get(state_machine_id),
			Some(1030)
		);
	})
}
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L895-933)
```rust
			let rotated = new_state.current_authorities.id > prev_state.current_authorities.id;

			// Messaging proofs must finalize a parachain head we haven't seen; one that doesn't
			// carries no new work and is rejected. Rotation proofs are exempt: the session
			// boundary justification carries whatever head the relay chain held at that block,
			// and if the parachain stalled for a session it is byte-for-byte the head the
			// previous proof already finalized. Failing here is a dispatch error, so it would
			// roll back the authority-set rotation `handle_incoming_message` just applied,
			// pinning the consensus state on the old set forever — the mandatory-block
			// justification is the only one a prover can obtain for that session, so every
			// retry fails identically.
			if !rotated && latest_height <= prev_height {
				Err(Error::<T>::StaleProof)?
			}

			let state_commitment = host
				.state_machine_commitment(StateMachineHeight {
					height: latest_height,
					id: StateMachineId {
						consensus_state_id: T::ConsensusStateId::get(),
						state_id: coprocessor,
					},
				})
				.unwrap_or_default();

			// Emit pallet-ismp events for all state machine updates
			for ev in events {
				pallet_ismp::Pallet::<T>::deposit_event(ev.into());
			}

			let child_trie_root =
				state_commitment.overlay_root.ok_or_else(|| Error::<T>::MissingChildTrieRoot)?;

			// Reject proofs that would be no-ops: no rotation and no new messages.
			let last_rewarded = LastRewardedDispatchRoot::<T>::get().unwrap_or_default();
			let has_new_messages = child_trie_root != last_rewarded && latest_height > prev_height;
			if !rotated && !has_new_messages {
				Err(Error::<T>::NoNewWork)?
			}
```

**File:** sdk/packages/core/contracts/vaults/StreamingYieldVault.sol (L186-203)
```text
    ///      must have already moved `amount` of `asset` into the vault (so `balanceOf` reflects it
    ///      before `_vestingAmount` is set, avoiding a transient `totalAssets` underflow).
    function _startVesting(uint256 amount) private {
        if (amount == 0) revert ZeroAmount();

        uint256 start = _vestingStart;
        if (start != 0) {
            if (block.timestamp < start + VEST) revert YieldStillVesting(start + VEST);
            // Hold off until the guaranteed deposit window has elapsed, so new capital always has
            // a chance to enter between tranches regardless of how promptly the keeper runs.
            if (block.timestamp < start + VEST + MIN_WINDOW) revert DepositWindowOpen(start + VEST + MIN_WINDOW);
        }

        _vestingAmount = amount;
        _vestingStart = block.timestamp;

        emit YieldAdded(amount, block.timestamp);
    }
```

**File:** modules/ismp/core/src/handlers/consensus.rs (L41-80)
```rust
	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
	host.store_consensus_state(msg.consensus_state_id, new_state)?;
	let timestamp = host.timestamp();
	host.store_consensus_update_time(msg.consensus_state_id, timestamp)?;
	let mut state_updates = vec![];
	for (id, mut commitment_heights) in intermediate_states {
		commitment_heights.sort_unstable_by(|a, b| a.height.cmp(&b.height));
		let previous_latest_height = host.latest_commitment_height(id)?;
		let mut last_commitment_height = None;
		for commitment_height in commitment_heights.iter() {
			let state_height = StateMachineHeight { id, height: commitment_height.height };

			// Only allow heights greater than latest height
			if previous_latest_height > commitment_height.height {
				continue;
			}

			// Skip duplicate states
			if host.state_machine_commitment(state_height).is_ok() {
				continue;
			}

			last_commitment_height = Some(state_height);
			host.store_state_machine_commitment(state_height, commitment_height.commitment)?;
			host.store_state_machine_update_time(state_height, host.timestamp())?;
		}

		if let Some(latest_height) = last_commitment_height {
			let latest_height = StateMachineHeight { id, height: latest_height.height };
			state_updates.push(Event::StateMachineUpdated(StateMachineUpdated {
				state_machine_id: id,
				latest_height: latest_height.height,
			}));
			host.store_latest_commitment_height(latest_height)?;
		}
```
