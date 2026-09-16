## Title
Relayer fee withdrawal zeroes `Fees` before the destination-side payout is confirmed, permanently losing the fee if the transfer fails — (File: `modules/pallets/relayer/src/withdrawal.rs`)

### Summary
Analogous to the C4 finding where `safeRewardTransfer` optimistically marked rewards as paid before confirming the underlying token transfer succeeded (causing silent, permanent loss when the contract lacked funds), `pallet-relayer`'s `withdraw()` zeros a relayer's accrued `Fees` balance immediately after *dispatching* a cross-chain payout request — not after confirming it was actually executed/paid on the destination.

### Finding Description
`Pallet::withdraw` in `modules/pallets/relayer/src/withdrawal.rs` reads the relayer's `available_amount` from `Fees`, dispatches an ISMP `PostRequest` instructing the destination to pay it out, and then unconditionally zeroes the source-side accounting: [1](#0-0) 

`dispatcher.dispatch_request(...)` only proves that the withdrawal *message was queued/committed* for delivery — it says nothing about whether the destination will actually be able to pay. On a substrate destination, the payload is routed to the built-in `HyperbridgeWithdrawalModule::on_accept`, which performs the real payout via `T::Currency::transfer` from `RELAYER_FEE_ACCOUNT`: [2](#0-1) 

If `RELAYER_FEE_ACCOUNT` (the fee escrow on the destination chain) is under-funded — e.g. due to accounting drift, a race between multiple pending withdrawals draining the same account, or simply because it was never topped up to cover this specific chain's relayer accruals — `T::Currency::transfer` fails and `on_accept` returns `Err`. Unlike a request *timeout* (which pallet-ismp explicitly refunds per the dispatcher's own doc comment: "If the dispatched request times-out, then pallet-ismp's inner subsystems will refund the fees to the sponsor"), a *delivered-but-failed-execution* POST request has no such refund path back to `Fees` on the source (hyperbridge) chain. The `Fees` entry was already zeroed at dispatch time, so the relayer has no way to re-claim the amount, and there is no retry that restores the pre-dispatch accounting.

### Impact Explanation
This is a direct, permanent loss of relayer fee funds reachable by any relayer calling the unsigned `withdraw` extrinsic — no privileged actor is required. The relayer's legitimately earned, accounted-for fee balance is destroyed on the optimistic assumption that the dispatched payout message will always succeed on the destination. If the destination-side escrow account is ever under-funded relative to a specific withdrawal (which the relayer pallet itself cannot verify before dispatch, since it has no visibility into the destination's live balance), the fee is unrecoverably lost, exactly mirroring the "loss of funds due to un-reverted/optimistic settlement before transfer success is confirmed" bug class from the referenced report.

### Likelihood Explanation
Likelihood is moderate: `RELAYER_FEE_ACCOUNT` balances on destination chains are funded from application-level fee payments and are not guaranteed to always exceed every individual relayer's accrued (and simultaneously withdrawing) balance, especially under concurrent withdrawals or accounting edge cases across many relayers/chains. No attacker action is needed — this can occur through ordinary operation whenever escrow funding lags accrued relayer claims.

### Recommendation
Do not zero `Fees` at dispatch time. Instead, either (a) zero it only after receiving confirmation that the destination executed the payout (e.g., via a response/ack message back to the relayer pallet), or (b) keep a pending/reserved amount that is restored if the destination signals a failed execution (mirroring the existing timeout-refund pattern), so a failed transfer on the destination does not translate into an unrecoverable loss of the relayer's accounted fee.

### Proof of Concept
1. A relayer accrues `Fees[dest_chain][relayer] = X` on hyperbridge from prior message deliveries.
2. `RELAYER_FEE_ACCOUNT` on `dest_chain` currently holds less than `X` (e.g., due to concurrent withdrawals by other relayers draining it, or delayed top-up).
3. The relayer calls `withdraw()`; `dispatch_request` succeeds (message queued) and `Fees` is zeroed immediately: [3](#0-2) .
4. The message is later delivered to `dest_chain`; `HyperbridgeWithdrawalModule::on_accept` calls `T::Currency::transfer(&RELAYER_FEE_ACCOUNT, &account, amount, ...)`, which fails because the account balance is insufficient, returning `Err`: [4](#0-3) .
5. The relayer receives no payout and has no accrued `Fees` balance left to re-withdraw — the amount `X` is permanently lost.

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L169-187)
```rust
		// Account is not useful in this case
		dispatcher
			.dispatch_request(
				DispatchRequest::Post(post),
				FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() },
			)
			.map_err(|_| Error::<T>::DispatchFailed)?;

		Fees::<T>::insert(withdrawal_data.dest_chain, address.clone(), U256::zero());

		Self::deposit_event(Event::<T>::Withdraw {
			address: sp_runtime::BoundedVec::truncate_from(address.clone()),
			beneficiary_address: sp_runtime::BoundedVec::truncate_from(beneficiary_address),
			state_machine: withdrawal_data.dest_chain,
			amount: available_amount,
		});

		Ok(())
	}
```

**File:** modules/pallets/ismp/src/dispatcher.rs (L189-213)
```rust
impl<T: Config> IsmpModule for HyperbridgeWithdrawalModule<T> {
	fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
		// Only the configured coprocessor may instruct withdrawals.
		let source = request.source;
		if Some(source) != T::Coprocessor::get() {
			Err(IsmpError::Custom(format!("Invalid request source: {source}")))?
		}

		let message = Message::<T::AccountId, T::Balance>::decode(&mut &request.body[..])
			.map_err(|err| IsmpError::Custom(format!("Failed to decode message: {err:?}")))?;

		match message {
			Message::WithdrawRelayerFees(WithdrawalRequest { account, amount }) => {
				T::Currency::transfer(
					&RELAYER_FEE_ACCOUNT.into_account_truncating(),
					&account,
					amount,
					Preservation::Expendable,
				)
				.map_err(|err| {
					IsmpError::Custom(format!("Error withdrawing protocol fees: {err:?}"))
				})?;

				Pallet::<T>::deposit_event(Event::<T>::RelayerFeeWithdrawn { amount, account });
			},
```
