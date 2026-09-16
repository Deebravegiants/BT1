## Finding

### Title
Messaging BEEFY proofs permanently revert once the reward treasury is depleted, freezing Hyperbridge message delivery until manual top-up - (File: `modules/pallets/beefy-consensus-proofs/src/lib.rs`)

### Summary
`Pallet::settle_first_proof` in `pallet-beefy-consensus-proofs` pays a `ProofReward` from a `TreasuryPalletId`-derived account to every prover that lands a new *messaging* (non-rotation) BEEFY proof. If that treasury account's balance ever drops below `ProofReward`, the payout fails and — unlike the rotation path — the whole extrinsic is made to fail hard, so no further messaging proof can ever be accepted until an admin manually refills the treasury.

### Finding Description
`pay_position_reward` transfers `ProofReward` from the pallet's treasury account to the submitter on every accepted first proof: [1](#0-0) 

`settle_first_proof` branches on whether the proof rotated the authority set. For a rotation, a failed transfer is logged and swallowed so the already-applied rotation is never rolled back. For a *messaging* proof, the same failure is deliberately propagated as a hard error, reverting the extrinsic: [2](#0-1) 

This is confirmed by the pallet's own test, whose comments explicitly document the asymmetry as intentional design: rotations must not be blocked, but "messaging proofs deliberately keep the hard error": [3](#0-2) 

The treasury account is drained by ordinary operation — every accepted messaging (and rotation) proof pays out `ProofReward` — with no floor check before payout is attempted and no automatic disabling of rewards when the balance runs low. Once the treasury balance falls below `ProofReward`, `Currency::transfer` fails with `RewardTransferFailed`, and because messaging proofs propagate this as `Err(e)?`, **every subsequent messaging proof submission reverts**, regardless of how valid the underlying BEEFY/SP1 proof is.

Messaging proofs are how Hyperbridge's on-chain view of connected chains' new message commitments (child-trie roots feeding `LastRewardedDispatchRoot`, `MessagingProofs`, and ultimately request/response delivery) advances. Blocking them blocks the entire inbound message pipeline for every connected state machine, since rotation proofs (authority-set changes) are rare and unrelated to ordinary message flow.

### Impact Explanation
This is a permissionless, single-extrinsic-reachable freeze of message delivery: any account can call `submit_proof` (the underlying dispatchable) with a fully valid BEEFY/SP1 messaging proof, and it will unconditionally revert once the treasury balance is insufficient — with no way for provers to work around it, since the reward payout is not optional or skippable on this path. Only a privileged, out-of-band top-up of the treasury account (or lowering `ProofReward` to zero via `AdminOrigin`) restores the flow, exactly mirroring the referenced report's "blocked until manual intervention" pattern. This qualifies as "a route unable to deliver messages" under the accepted impact categories, since no new state advancement (and therefore no new message proofs) can land on Hyperbridge for any connected chain during the freeze.

### Likelihood Explanation
The treasury is a finite, governance-funded pool that pays out on every single accepted proof (both first-provers and uncles). Under sustained SP1 uncle-reward activity or simply steady operation without proactive top-ups, the treasury balance will trend toward depletion over time — this requires no malicious actor, governance error, or admin misconfiguration, only ordinary usage outpacing funding. Given BEEFY consensus proofs are the backbone of Hyperbridge's connection to every consensus client (BSC, sync-committee, GRANDPA, parachains, etc. via the coprocessor), this is a realistic, high-impact operational risk rather than a contrived edge case.

### Recommendation
Apply the same "reward is the cheaper thing to drop" treatment to messaging proofs that already exists for rotations: catch `RewardTransferFailed` (and any other reward-payout error) for messaging proofs too, log it, and continue applying the state advance with a zero reward, rather than reverting the whole extrinsic. Optionally, add a treasury balance floor/circuit breaker that automatically disables reward payout (treats `ProofReward` as effectively 0) once the treasury can't cover it, so message delivery is never coupled to treasury solvency.

### Proof of Concept
1. Deploy with `ProofReward` set to some non-zero value via `set_proof_reward`.
2. Do not fund (or drain) the `TreasuryPalletId`-derived account below `ProofReward`.
3. Submit any valid messaging (non-rotation) BEEFY/SP1 proof via `submit_proof`.
4. `settle_first_proof` calls `pay_position_reward`, which fails `Currency::transfer` with `RewardTransferFailed`; because `outcome.rotated == false`, `Err(e) => Err(e)?` propagates and the extrinsic reverts — as directly demonstrated by the pallet's own test `an_unpayable_reward_cannot_block_a_rotation`, whose second assertion shows the messaging-proof call returning `Err`: [4](#0-3) 
5. Every subsequent messaging proof submission fails identically until an admin either tops up the treasury or zeroes `ProofReward`.

### Citations

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L563-581)
```rust
			// Same reasoning as the uncle bookkeeping above: the caller has already applied the
			// authority-set rotation, so a hard error here rolls it back, and since the mandatory
			// justification is the only one obtainable for that session every retry fails
			// identically until someone tops the treasury up — leaving the consensus state on the
			// old set in the meantime. A missed reward is the cheaper loss, so log and carry on.
			// Messaging proofs keep the hard error: reverting one is recoverable, because the work
			// is re-attempted by the next proof once the treasury can pay.
			let reward_paid = match Self::pay_position_reward(&submitter, 0) {
				Ok(reward) => reward,
				Err(e) if outcome.rotated => {
					log::warn!(
						target: "ismp",
						"[beefy-consensus-proofs] reward skipped for rotation to set {}: {e:?}",
						outcome.current_set_id,
					);
					BalanceOf::<T>::default()
				},
				Err(e) => Err(e)?,
			};
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L733-757)
```rust
		fn pay_position_reward(
			submitter: &T::AccountId,
			position: u32,
		) -> Result<BalanceOf<T>, Error<T>> {
			let zero = BalanceOf::<T>::default();
			let base = ProofReward::<T>::get();
			if base == zero {
				return Ok(zero);
			}

			let reward = Self::position_reward(base, position);
			if reward == zero {
				return Ok(zero);
			}

			let treasury: T::AccountId =
				<T as Config>::TreasuryPalletId::get().into_account_truncating();
			<T as Config>::Currency::transfer(&treasury, submitter, reward, Preservation::Preserve)
				.map_err(|e| {
					log::warn!(
						target: "ismp",
						"[beefy-consensus-proofs] treasury reward transfer failed: {e:?}",
					);
					Error::<T>::RewardTransferFailed
				})?;
```

**File:** modules/pallets/testsuite/src/tests/pallet_beefy_consensus_proofs.rs (L188-232)
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

		assert_eq!(
			RotationProofs::<Test>::get().get(&30).copied(),
			Some(height),
			"the rotation must be recorded even though the reward could not be paid",
		);

		// The asymmetry is deliberate: reverting a messaging proof is recoverable, because the
		// next proof re-attempts the same work once the treasury can pay.
		assert!(
			pallet_beefy_consensus_proofs::Pallet::<Test>::settle_first_proof(
				submitter(12),
				vec![PROOF_TYPE_SP1, 0xac],
				Some(H256::repeat_byte(12)),
				PROOF_TYPE_SP1,
				Vec::new(),
				messaging_outcome(height + 1, 30),
			)
			.is_err(),
			"a messaging proof must still fail hard when the reward cannot be paid",
		);
```
