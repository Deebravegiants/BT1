## Title
Outbound relayer-reward claims accept a relayer-supplied `payee` with no zero-account check, permanently burning the reward - (File: `modules/pallets/relayer/src/outbound_request.rs`, `modules/pallets/relayer/src/outbound_consensus.rs`)

### Summary
`Pallet::process_outbound_request_delivery_claim` and `Pallet::process_outbound_consensus_delivery_claim` let the relayer who delivered a message pick an arbitrary `payee: [u8; 32]` to receive the treasury-funded delivery reward. Neither function validates that `payee` is non-zero before converting it to an `AccountId` and transferring funds, and both permanently mark the claim as consumed in the same call. A relayer that submits a valid claim with `payee = [0u8; 32]` irrecoverably burns their own reward, exactly mirroring the reported `BasePool#claimRewards` bug class ("allows users to burn rewards" via an unchecked, self-chosen zero receiver).

### Finding Description
In `outbound_request.rs`, the claim struct carries a free-form `payee`: [1](#0-0) 

The pallet verifies only that the signature recovers to the relayer address proven in the destination's receipt slot — it never checks `payee` itself — and then unconditionally transfers the reward and marks the commitment claimed: [2](#0-1) 

The same pattern exists in `outbound_consensus.rs`: `payee` is taken verbatim from the claim, converted to an `AccountId`, and the reward is transferred and the rotation marked claimed in the same extrinsic, with no zero-account guard: [3](#0-2) 

Both `OutboundRequestsClaimed::<T>::insert(commitment, ())` and `OutboundConsensusRotationsClaimed::<T>::insert(destination, set_id, ())` are permanent idempotency markers with no re-claim path — once a commitment/rotation is marked claimed, it can never be claimed again, even with a corrected `payee`. This is the on-chain equivalent of `BasePool#claimRewards(address(0))`: an unprivileged, permissionless call (`ensure_none(origin)` per the unsigned-extrinsic design documented in `docs/outbound-request-incentivization.md`) lets the caller nominate the fund destination with no sanity check, and a zero/burn value destroys the reward forever rather than reverting.

### Impact Explanation
The transferred amount is `OutboundRequestDeliveryReward[module_id]` or `OutboundConsensusDeliveryReward[destination]`, both governance-configured incentive amounts paid from the protocol `TreasuryPalletId` account. A relayer (or a buggy relayer client that zero-initializes its keypair/payee field before signing) that submits a claim with `payee = [0u8; 32]` causes:
- The treasury to permanently lose the reward amount (funds sent to an unrecoverable AccountId).
- The claim being marked as consumed, so the legitimate reward for that delivered request/rotation can never be claimed by anyone else afterward.

This is a concrete, permanent loss of protocol treasury funds and blocks the intended future issuance of that specific reward, satisfying "permanent freezing/loss of funds" for relayer reward accounting explicitly listed as in-scope.

### Likelihood Explanation
Any relayer that successfully delivers a hyperbridge-originated request or a mandatory consensus rotation can trigger this by constructing a claim with `payee = [0u8; 32]` — no privileged role, governance approval, or special conditions are required beyond having already legitimately performed a delivery (which is the normal, expected relayer workflow). It can also occur accidentally from client-side bugs that fail to populate the payee before signing, since nothing on-chain rejects it.

### Recommendation
Add an explicit check that `payee != [0u8; 32]` (and ideally that it decodes to a valid, non-dead `AccountId`) at the start of `process_outbound_request_delivery_claim` and `process_outbound_consensus_delivery_claim`, rejecting the claim with a dedicated error (e.g. `Error::<T>::InvalidPayee`) before any state mutation or idempotency marker is written, so a bad `payee` doesn't consume the claim.

### Proof of Concept
1. Relayer delivers a hyperbridge-originated `PostRequest` (or a mandatory consensus rotation) to a destination chain, becoming the address recorded in `RequestReceipts[commitment]` (or `EvmHost._epochs[set_id]`).
2. Relayer builds a valid `OutboundRequestDeliveryClaim` (or `OutboundConsensusDeliveryClaim`), signing `outbound_request_delivery_message(commitment, destination, payee)` with `payee = [0u8; 32]`.
3. Submits `claim_outbound_request_delivery_reward` (unsigned, `ensure_none` origin) via `pallet-ismp-relayer`.
4. All pipeline checks pass (source check, commitment presence, allowlist reward > 0, state proof, signature recovery match). `payee_account: T::AccountId = [0u8;32].into()` receives the treasury transfer, and `OutboundRequestsClaimed::<T>::insert(commitment, ())` is written.
5. The reward is unrecoverable (sent to an account no one controls) and the commitment can never be claimed again.

### Citations

**File:** modules/pallets/relayer/src/outbound_request.rs (L96-105)
```rust
	pub state_proof: Proof,
	/// Sr25519 public key on Hyperbridge that the reward is paid to.
	pub payee: [u8; 32],
	/// Signature over [`outbound_request_delivery_message`] of
	/// `(commitment, destination, payee)`. For EVM destinations the recovered
	/// secp256k1 address must equal the address proven in the receipt slot;
	/// for substrate destinations the recovered signer bytes must equal the
	/// relayer bytes proven in the receipt slot.
	pub signature: Signature,
}
```

**File:** modules/pallets/relayer/src/outbound_request.rs (L171-194)
```rust
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
```

**File:** modules/pallets/relayer/src/outbound_consensus.rs (L174-196)
```rust
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

		OutboundConsensusRotationsClaimed::<T>::insert(destination, set_id, ());

		Self::deposit_event(Event::OutboundConsensusDeliveryRewarded {
			state_machine: destination,
			set_id,
			relayer: payee_account,
			amount: reward,
		});

```
