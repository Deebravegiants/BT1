Based on my investigation, I found a genuine analog to the "zero balance" reward-distribution bug class in `pallet-beefy-consensus-proofs`.

### Title
Messaging-proof settlement hard-fails on empty/insufficient treasury balance, permanently blocking cross-chain message delivery via BEEFY - ([File: modules/pallets/beefy-consensus-proofs/src/lib.rs])

### Summary
`pallet-beefy-consensus-proofs::settle_first_proof` deliberately hard-fails (propagates the error, reverting the whole extrinsic) when the reward treasury cannot pay the configured `ProofReward` — including the case where the treasury balance is zero. Because BEEFY consensus proof acceptance and cross-chain messaging-proof acceptance are settled inside the *same* extrinsic, a zero/insufficient treasury balance blocks the messaging proof from ever being accepted, which stalls delivery of all cross-chain messages riding on that proof.

### Finding Description
`pay_position_reward` reads the treasury balance implicitly via `T::Currency::transfer` and maps any transfer failure (including "treasury has zero/insufficient balance") to `Error::<T>::RewardTransferFailed`: [1](#0-0) 

In `settle_first_proof`, this error is explicitly swallowed only for the **rotation** case (authority-set change), with an inline comment stating the design intends messaging proofs to keep the hard error: [2](#0-1) 

The pallet's own unit test confirms and documents this exact asymmetry — a treasury with a **zero balance in genesis** causes any non-zero `ProofReward` to make `settle_first_proof` fail for a messaging proof (while a rotation is exempted): [3](#0-2) 

This is structurally the same bug class as the Lido report: a reward-distribution code path is entangled with an unrelated critical operation (here, cross-chain message delivery) and is not guarded against the treasury having a zero balance, so the critical operation fails whenever the reward cannot be paid.

### Impact Explanation
Once `ProofReward` is configured (governance sets a non-zero value) and the treasury account's balance drops to zero or below the reward amount (e.g., through legitimate payouts draining it, or simply never being funded), every subsequent messaging BEEFY proof submission reverts with `RewardTransferFailed`. Since messaging proofs are the mechanism by which Hyperbridge extends trust in cross-chain state and propagates dispatch roots for message delivery, this halts the flow of all cross-chain messages relying on BEEFY consensus proofs until an operator notices and tops up the treasury — a protocol-wide denial of service on message delivery, matching the "route unable to deliver messages" acceptance criterion.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: the treasury is a shared pool that also pays out `pallet-relayer` outbound-consensus/outbound-request rewards, `pallet-collator-manager` rewards, and other treasury-funded flows (see `TreasuryPalletId`/`TreasuryAccount` usages across `outbound_consensus.rs`, `outbound_request.rs`, `collator-manager`). Any operational failure to keep the treasury funded, or a spike in reward payouts elsewhere draining the shared account, silently starts blocking messaging-proof acceptance with no automatic recovery — recovery requires an off-chain governance top-up action.

### Recommendation
Apply the same tolerant-failure pattern already used for rotations to messaging proofs: log-and-continue (drop the reward but still accept the proof) rather than reverting settlement, or explicitly check the treasury's spendable balance against the configured `ProofReward` before attempting the transfer and skip payment gracefully when insufficient, so that the reward-payment path can never block message delivery.

### Proof of Concept
1. Deploy the runtime with `pallet-beefy-consensus-proofs` and leave the treasury account (`TreasuryPalletId::get().into_account_truncating()`) unfunded (balance `0`).
2. Governance sets `ProofReward` to a non-zero value via the pallet's configured origin.
3. Submit any valid messaging BEEFY proof (naive or SP1) via `submit_proof` → `do_submit_proof` → `verify_and_apply` succeeds → `settle_first_proof` is called with `outcome.rotated == false`.
4. `pay_position_reward` calls `T::Currency::transfer(&treasury, &submitter, reward, Preservation::Preserve)`, which fails because treasury balance is `0`.
5. `settle_first_proof` matches `Err(e) => Err(e)?` (not the rotation branch), so the whole extrinsic reverts with `RewardTransferFailed` — the state advancement and dispatch-root propagation from `verify_and_apply` is rolled back, and the message never gets recorded as deliverable.
6. This is reproduced verbatim by the existing repo test `an_unpayable_reward_cannot_block_a_rotation`, whose second half explicitly asserts `settle_first_proof(...).is_err()` for a messaging proof under a zero-balance treasury: [4](#0-3)

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

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L748-757)
```rust
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
