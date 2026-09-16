Based on my investigation, I found the analog in `pallet-beefy-consensus-proofs`.

### Title
Messaging BEEFY Proof Submission Reverts and Rolls Back State Commitment When Treasury Reward Payment Fails - ([File: modules/pallets/beefy-consensus-proofs/src/lib.rs])

### Summary
The messaging-proof settlement path in `pallet-beefy-consensus-proofs` calls `Self::pay_position_reward(&submitter, 0)` after the BEEFY/SP1 consensus proof has already been cryptographically verified and the new parachain state commitment applied via `handlers::handle_incoming_message`. For rotation proofs the code explicitly tolerates a reward-payment failure ("log and carry on"), but for messaging proofs it propagates the error with `Err(e)?`, which is a hard `DispatchError` that rolls back the entire extrinsic — including the state-machine commitment update that `verify_and_apply` just persisted.

### Finding Description
This mirrors the Synthetix bug class: a side-effect bookkeeping/reward operation embedded inside a critical operation can revert and take down the whole operation, even though the primary purpose of the call (advancing consensus/minting/dispatching) was already validly completed. Here, `submit_proof` calls `Self::verify_and_apply(&proof)`, which internally calls `handlers::handle_incoming_message` and persists the new `StateCommitment` for the destination parachain height into `pallet-ismp` storage. After that succeeds, the pallet attempts `Self::pay_position_reward(&submitter, 0)`: [1](#0-0) 
The comment at line 568 makes the design intent explicit: "Messaging proofs keep the hard error: reverting one is recoverable, because the work is re-attempted by the next proof once the treasury can pay." But this reasoning conflates dispatch-level atomicity with actual recoverability. If `pay_position_reward` fails for a systemic reason (e.g., treasury underfunded, which the code elsewhere explicitly anticipates as a real failure mode — see `docs/outbound-request-incentivization.md` "That account must hold enough balance or the claim fails"), then **every future call to `submit_proof` for a messaging proof will hit the identical treasury shortfall and revert identically**, since Substrate transaction failure rolls back all storage writes performed during dispatch, including the just-verified state commitment. This is functionally identical to `notifyRewardAmount()` reverting and blocking `Synthetix.mint()`: a reward-accounting subroutine that legitimately can fail under normal operating conditions is allowed to abort an unrelated, already-completed critical state transition (consensus commitment delivery), rather than being isolated so its failure is merely a missed reward.

### Impact Explanation
This is reachable by any unprivileged off-chain prover/relayer submitting a signed `submit_proof` extrinsic — no privileged role required. If the treasury balance backing consensus-proof rewards is ever insufficient (a realistic, non-adversarial, non-privileged condition — treasuries drain over time from reward payouts), every messaging proof submission for that path reverts, and the parachain's state commitment on Hyperbridge can never be advanced for messages routed through that consensus client, even though a cryptographically valid proof is being supplied repeatedly. This satisfies "a route unable to deliver messages" — new POST/GET requests and responses relying on that state commitment cannot be delivered or timed out until the treasury is manually topped up, a form of protocol-level denial of service on message delivery caused by an unrelated financial precondition.

### Likelihood Explanation
Medium-to-High. Treasury depletion is not a contrived edge case — mandatory rotation proofs, uncle rewards, and messaging-proof rewards are all continuously drawn from the same treasury account (`T::TreasuryAccount`) referenced throughout this pallet and `consensus-incentives`. Any period of high proof volume, misconfigured reward rate, or delayed top-up governance action would trigger this path deterministically, and once triggered it self-perpetuates (every subsequent submission fails identically) until an admin action funds the treasury — exactly the "erroneous rewards / gap between periods" style failure called out in the reference report.

### Recommendation
Decouple reward payment from the consensus-commitment write for messaging proofs, matching the tolerant handling already used for rotation proofs: if `pay_position_reward` fails, log a warning and set `reward_paid = 0` rather than propagating the error, so the already-valid state commitment is persisted regardless of treasury solvency. Reward accounting should never be able to block or roll back delivery of a validly proven consensus update.

### Proof of Concept
1. Drain (or never adequately fund) the treasury account backing `pallet-beefy-consensus-proofs` reward payouts.
2. An off-chain prover submits a valid messaging BEEFY/SP1 proof via `submit_proof`, advancing the latest proven parachain height past a block containing new ISMP requests.
3. `verify_and_apply` succeeds, verifying the proof and internally applying the new `StateCommitment` via `handle_incoming_message`.
4. `Self::pay_position_reward(&submitter, 0)` fails due to insufficient treasury funds; since `outcome.rotated` is `false` for a messaging proof, the `Err(e)?` branch at [2](#0-1)  is taken, causing the whole extrinsic to revert.
5. The state commitment that was about to be persisted is rolled back with the rest of the dispatch. Repeat submission of the same (or any later) valid proof fails identically until the treasury is refunded, permanently stalling message delivery for that destination.

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
