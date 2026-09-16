## Analysis

The Sherlock finding describes a pattern where an admin action zeroes an eligibility flag (`currentAllocations[protocol] = 0`) *before* pending rewards tied to that flag are claimed, permanently forfeiting funds that had already legitimately accrued. Hyperbridge's outbound-delivery reward system on `pallet-relayer` reproduces this exact pattern.

`OutboundRequestDeliveryReward` doubles as both the per-module reward amount *and* the allowlist flag — the pallet's own doc comment says a module with zero reward is "treated as not on the allowlist." [1](#0-0) 

The claim path enforces this at claim time, not at delivery time: [2](#0-1) 

Governance can update this value at any time via `set_outbound_request_delivery_reward`: [3](#0-2) 

The identical shape exists for consensus-rotation rewards, where `OutboundConsensusDeliveryReward` is checked only after all the expensive state-proof verification, right before payout: [4](#0-3) 

A relayer that has already delivered a hyperbridge-originated request or a mandatory consensus rotation (real, verifiable on-chain work, proven by the `RequestReceipts`/`_epochs` state proof) has no claim window guarantee: if governance re-prices or disables the module/chain's reward (e.g., deprecating a module, adjusting economics) between delivery and the relayer's claim submission, `reward` reads back as `0` and the claim is rejected with `OutboundRequestNoRewardConfigured` / `OutboundNoRewardConfigured`, and the relayer's earned reward for that specific delivery is unrecoverable — there is no fallback path, no snapshot of the reward rate at delivery time, and no reservation of treasury funds at delivery time.

This mirrors the Vault bug precisely: `blacklistProtocol` zeroes `currentAllocations` (the allocation is analogous to the reward-eligibility flag) before `claimTokens` reads it, permanently losing the harvest that had already accrued. Here, `set_outbound_request_delivery_reward(module_id, 0)` (or lowering `OutboundConsensusDeliveryReward`) zeroes the same value the claim function gates on, permanently losing rewards for deliveries that already happened and are provably on-chain.

### Title
Outbound-reward zeroing before claim permanently forfeits already-earned relayer rewards - (modules/pallets/relayer/src/outbound_request.rs, modules/pallets/relayer/src/outbound_consensus.rs)

### Summary
`process_outbound_request_delivery_claim` and `process_outbound_consensus_delivery_claim` read the *current* value of `OutboundRequestDeliveryReward` / `OutboundConsensusDeliveryReward` at claim time rather than snapshotting the reward rate in effect when the relayer actually performed the delivery. Because the reward amount also serves as the module/chain allowlist flag (zero = not allowed), any governance update that lowers or zeroes the reward after a delivery but before the relayer claims it permanently forfeits that relayer's already-earned payout, with no error recovery path.

### Finding Description
`OutboundRequestDeliveryReward::<T>::get(&module_id)` is read fresh inside `process_outbound_request_delivery_claim`, well after the pallet has already confirmed (via `RequestCommitments`, source check, and the destination state proof of `RequestReceipts[commitment]`) that the relayer genuinely delivered the request: [5](#0-4) 

The same happens for consensus-rotation rewards in `process_outbound_consensus_delivery_claim`, where the reward check occurs even after signature verification succeeds, confirming genuine delivery: [6](#0-5) 

Both setters that mutate the reward value are unconditionally available to governance at any time, with no check for outstanding un-claimed deliveries for that key: [7](#0-6) 

Because delivery (which the relayer completes off-chain against a destination chain, and which the design doc explicitly frames as a race relayers compete for) and claim (a separate later transaction on Hyperbridge) are decoupled steps, there is necessarily a window between them: [8](#0-7) 

If the reward for that `module_id`/destination is changed during that window, the relayer's claim for a delivery it already performed under the old reward rate fails outright (`OutboundRequestNoRewardConfigured` / `OutboundNoRewardConfigured`), and there is no accounting mechanism (e.g., a reward-rate snapshot recorded at dispatch/delivery time, or a grace-period reservation) to make the relayer whole. This is structurally the same defect as the reported Vault bug: an eligibility/amount flag is mutated without first settling (claiming) whatever had already accrued against it.

### Impact Explanation
This is a fund-freezing/loss bug for the relayer incentive layer: the reward transfer that should occur from the treasury to the relayer never happens for deliveries caught in this window, and the relayer has no path to recover it. Since delivery is itself a race relayers compete for and pay gas/opportunity cost to win, this converts the reward from "guaranteed once delivered" to "conditional on governance not touching the rate before the claim lands," undermining the entire incentive design documented in `outbound-request-incentivization.md`. Given the treasury is expected to hold the reward funds ready for payout, this is a concrete loss of funds owed rather than merely a griefing/DoS issue.

### Likelihood Explanation
Reward-rate/allowlist updates via `set_outbound_request_delivery_reward` and `set_outbound_consensus_delivery_reward` are expected, ordinary governance operations (adding/removing modules from the incentive program, retuning economics), not a rare edge case — the design doc itself frames modules being added/removed from the allowlist as normal lifecycle. Any relayer whose claim transaction is delayed (network congestion, waiting on `wait_for_state_machine_update`/challenge period as the claim tasks do) relative to a routine reward update is exposed. Given the multi-step, latency-bound claim pipeline (state-machine update wait, challenge period, proof construction), the window is non-trivial.

### Recommendation
Snapshot the reward amount at the time the request/rotation is recorded as claimable (e.g., store the reward rate alongside `RequestCommitments`/at dispatch time, or alongside the pending claim state) rather than re-reading the live, governance-mutable value at claim time. Alternatively, require `set_outbound_request_delivery_reward`/`set_outbound_consensus_delivery_reward` to only take effect after a delay, or disallow lowering the reward for a module/chain while any of its dispatched-but-unclaimed commitments still exist.

### Proof of Concept
1. Governance sets `OutboundRequestDeliveryReward[module_id] = R` via `set_outbound_request_delivery_reward`.
2. A pallet (e.g., host-executive) dispatches a `PostRequest` with `from = module_id`; `RequestCommitments` records it.
3. A relayer delivers this request to the destination chain, and the destination host records the relayer's address in `RequestReceipts[commitment]`.
4. Before the relayer submits `claim_outbound_request_delivery_reward`, governance calls `set_outbound_request_delivery_reward(module_id, 0)` (e.g., deprecating the module).
5. The relayer submits its claim with a valid state proof of delivery; `process_outbound_request_delivery_claim` reaches `let reward = OutboundRequestDeliveryReward::<T>::get(&module_id); ensure!(reward > 0, ...)` and rejects with `OutboundRequestNoRewardConfigured`, even though delivery is cryptographically proven.
6. The relayer's earned reward for this delivery is permanently lost; the commitment is not marked claimed, so re-submission after the rate is possibly restored still fails unless the exact original amount is restored, and there is no compensating mechanism regardless.

### Citations

**File:** modules/pallets/relayer/src/outbound_request.rs (L54-59)
```rust
/// Claim payload for [`Pallet::claim_outbound_request_delivery_reward`].
///
/// Carries the full [`PostRequest`] so the pallet can hash it on chain and
/// look up the reward by `request.from`. A module with zero reward is
/// treated as not on the allowlist and rejected before any state proof
/// verification runs.
```

**File:** modules/pallets/relayer/src/outbound_request.rs (L119-197)
```rust
	pub fn process_outbound_request_delivery_claim(
		claim: OutboundRequestDeliveryClaim,
	) -> DispatchResult {
		let OutboundRequestDeliveryClaim { request, state_proof, payee, signature } = claim;
		let destination = state_proof.height.id.state_id;

		let commitment = hash_request::<<T as Config>::IsmpHost>(&Request::Post(request.clone()));

		let host = <T as Config>::IsmpHost::default();
		ensure!(
			request.source == host.host_state_machine(),
			Error::<T>::OutboundRequestSourceNotHyperbridge,
		);

		ensure!(
			RequestCommitments::<T>::get(commitment).is_some(),
			Error::<T>::OutboundRequestNotKnown,
		);

		ensure!(
			!OutboundRequestsClaimed::<T>::contains_key(commitment),
			Error::<T>::OutboundRequestAlreadyClaimed,
		);

		let module_id: BoundedVec<u8, ModuleIdBound> = request
			.from
			.clone()
			.try_into()
			.map_err(|_| Error::<T>::OutboundRequestModuleIdTooLong)?;
		let reward = OutboundRequestDeliveryReward::<T>::get(&module_id);
		ensure!(reward > BalanceOf::<T>::default(), Error::<T>::OutboundRequestNoRewardConfigured);

		ensure!(destination == request.dest, Error::<T>::MismatchedStateMachine);

		let state_machine = ismp::handlers::validate_state_machine(&host, state_proof.height)
			.map_err(|_| Error::<T>::OutboundDestinationStateNotKnown)?;
		let receipt_key = state_machine
			.receipts_state_trie_key(vec![commitment])
			.into_iter()
			.next()
			.ok_or(Error::<T>::OutboundRequestUnsupportedDestination)?;
		let proof_results =
			Self::verify_withdrawal_proof(&*state_machine, &state_proof, vec![receipt_key.clone()])
				.map_err(|_| Error::<T>::OutboundDestinationStateNotKnown)?;
		let raw = proof_results
			.get(&receipt_key)
			.cloned()
			.flatten()
			.ok_or(Error::<T>::OutboundDeliveryNotProven)?;

		let delivered_by = Self::decode_receipt_relayer(destination, &raw)?;

		let msg = outbound_request_delivery_message(commitment, destination, payee);
		let recovered = signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
		ensure!(recovered == delivered_by, Error::<T>::OutboundRequestSignerMismatch);

		let treasury: T::AccountId =
			<T as Config>::TreasuryPalletId::get().into_account_truncating();
		let payee_account: T::AccountId = payee.into();
		<<T as pallet_ismp::Config>::Currency as Mutate<T::AccountId>>::transfer(
			&treasury,
			&payee_account,
			reward,
			Preservation::Preserve,
		)
		.map_err(|_| Error::<T>::OutboundRequestRewardTransferFailed)?;

		OutboundRequestsClaimed::<T>::insert(commitment, ());

		Self::deposit_event(Event::OutboundRequestDeliveryRewarded {
			commitment,
			state_machine: destination,
			module_id,
			relayer: payee_account,
			amount: reward,
		});

		Ok(())
	}
```

**File:** modules/pallets/relayer/src/lib.rs (L96-109)
```rust
	{
		/// The underlying [`IsmpHost`] implementation
		type IsmpHost: IsmpHost + IsmpDispatcher<Account = Self::AccountId, Balance = Self::Balance>;

		/// Origin for privileged actions
		type RelayerOrigin: EnsureOrigin<Self::RuntimeOrigin>;

		/// Treasury account derivation. Outbound consensus delivery rewards
		/// are transferred from the account derived from this `PalletId`.
		/// The treasury must be funded in the same currency as
		/// `pallet-ismp::Config::Currency`.
		#[pallet::constant]
		type TreasuryPalletId: Get<PalletId>;
	}
```

**File:** modules/pallets/relayer/src/lib.rs (L399-415)
```rust
		/// Governance-set per-chain reward for delivering mandatory consensus
		/// proofs to that destination.
		#[pallet::call_index(4)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(0, 1))]
		pub fn set_outbound_consensus_delivery_reward(
			origin: OriginFor<T>,
			state_machine: StateMachine,
			amount: BalanceOf<T>,
		) -> DispatchResult {
			T::RelayerOrigin::ensure_origin(origin)?;
			OutboundConsensusDeliveryReward::<T>::insert(state_machine, amount);
			Self::deposit_event(Event::OutboundConsensusDeliveryRewardUpdated {
				state_machine,
				new_reward: amount,
			});
			Ok(())
		}
```

**File:** modules/pallets/relayer/src/outbound_consensus.rs (L164-186)
```rust
		let evm_address = Self::decode_epochs_slot_address(destination, &raw)
			.ok_or(Error::<T>::OutboundDeliveryNotProven)?;

		// Replay protection comes from the `OutboundConsensusRotationsClaimed`
		let msg = outbound_consensus_delivery_message(set_id, destination, payee);
		let recovered = signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
		let recovered_address = Address::try_from(recovered.as_slice())
			.map_err(|_| Error::<T>::OutboundSignerMismatch)?;
		ensure!(recovered_address == evm_address, Error::<T>::OutboundSignerMismatch);

		let reward = OutboundConsensusDeliveryReward::<T>::get(destination);
		ensure!(reward > BalanceOf::<T>::default(), Error::<T>::OutboundNoRewardConfigured);

		let treasury: T::AccountId =
			<T as Config>::TreasuryPalletId::get().into_account_truncating();
		let payee_account: T::AccountId = payee.into();
		<<T as pallet_ismp::Config>::Currency as Mutate<T::AccountId>>::transfer(
			&treasury,
			&payee_account,
			reward,
			Preservation::Preserve,
		)
		.map_err(|_| Error::<T>::OutboundRewardTransferFailed)?;
```

**File:** docs/outbound-request-incentivization.md (L360-364)
```markdown

### Why testnet delivery is a race

The reward goes to whichever relayer lands the delivery transaction on the destination chain first. That relayer's address is what the destination's ISMP host writes into `RequestReceipts[commitment]`, and `process_outbound_request_delivery_claim` only pays the address proven in that slot. A relayer that delivers second just no-ops, and its claim fails `OutboundRequestSignerMismatch`. The on-chain reward is registered globally, so every relayer watching gargantua sees the module in its allowlist snapshot and competes. Running locally sidesteps this: your relayer is the only one delivering.

```
