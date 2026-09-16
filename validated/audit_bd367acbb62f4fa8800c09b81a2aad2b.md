Based on my analysis, I did not find a valid analog to CVE-2021-25281 in this codebase.

The SaltStack CVE's bug class is an **inconsistency between authorization paths**: the synchronous `wheel` client enforced eauth credentials, but the async variant (`wheel_async`) forgot to apply the same check, letting privileged wheel modules run unauthenticated.

I checked all comparable "async"/unsigned dispatch paths in Hyperbridge for the same inconsistency pattern:

- `pallet_ismp::Call::handle_unsigned` calls `ensure_none(origin)?` and is gated by `ValidateUnsigned::validate_unsigned`, which requires the batch to pass full proof verification via `Self::execute(messages)` before entering the transaction pool. [1](#0-0) [2](#0-1) 
- `pallet_ismp_relayer`'s unsigned calls (`accumulate_fees`, `withdraw_fees`, `claim_outbound_consensus_delivery_reward`) all likewise call `ensure_none(origin)?` and are proof-gated in `validate_unsigned`. [3](#0-2) 
- `pallet-call-decompressor`'s `validate_unsigned` re-derives the inner call and only allows `handle_unsigned` / `accumulate_fees` through, delegating to each pallet's own `validate_unsigned` — so it doesn't introduce a bypass of its own.
<invoke name="grep_search">
<parameter name="pattern">restrict\(</parameter>
<parameter name="repo_name">Alyssadaypin/hyperbridge--007</parameter>
<parameter name="include">*.sol</parameter>
</invoke>

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L614-625)
```rust
		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			use ismp::{
				messaging::{hash_request, ConsensusMessage, FraudProofMessage, RequestMessage},
				router::Request,
			};
			let messages = match call {
				Call::handle_unsigned { messages } => messages,
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};

			let events =
				Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;
```

**File:** modules/pallets/relayer/src/lib.rs (L350-397)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight({1_000_000})]
		pub fn accumulate_fees(
			origin: OriginFor<T>,
			withdrawal_proof: WithdrawalProof,
		) -> DispatchResult {
			ensure_none(origin)?;
			Self::accumulate(withdrawal_proof)
		}

		#[pallet::call_index(1)]
		#[pallet::weight({1_000_000})]
		pub fn withdraw_fees(
			origin: OriginFor<T>,
			withdrawal_data: WithdrawalInputData,
		) -> DispatchResult {
			ensure_none(origin)?;
			Self::withdraw(withdrawal_data)
		}

		/// Sets the minimum withdrawal amount using the correct decimals
		#[pallet::call_index(2)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(0, 1))]
		pub fn set_minimum_withdrawal(
			origin: OriginFor<T>,
			state_machine: StateMachine,
			amount: u128,
		) -> DispatchResult {
			T::RelayerOrigin::ensure_origin(origin)?;
			MinimumWithdrawalAmount::<T>::insert(state_machine, U256::from(amount));
			Ok(())
		}

		/// Pay the configured `OutboundConsensusDeliveryReward` to the EVM
		/// relayer attributed in the destination's `EvmHost._epochs[set_id]`.
		///
		/// Unsigned. Spam-protected by `validate_unsigned` (the encoded
		/// payload becomes a unique tag, so a duplicate submission with the
		/// same `(destination, set_id)` is rejected at the txpool stage).
		#[pallet::call_index(3)]
		#[pallet::weight({1_000_000})]
		pub fn claim_outbound_consensus_delivery_reward(
			origin: OriginFor<T>,
			claim: OutboundConsensusDeliveryClaim,
		) -> DispatchResult {
			ensure_none(origin)?;
			Self::process_outbound_consensus_delivery_claim(claim)
		}
```
