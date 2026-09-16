### Title
Missing event emission in `pallet_ismp::fund_message` after fee top-up and fund transfer - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
The `fund_message` extrinsic in `pallet-ismp` transfers currency from a caller into the `RELAYER_FEE_ACCOUNT` and increases the stored fee on a pending request/response commitment, but it never deposits an event to signal that this sensitive state change occurred. This mirrors the reported analog: a function that performs consequential state and balance changes (funding rate, timestamps, reward transfer) without emitting corresponding events, leaving off-chain relayers/indexers unable to reliably track and react to the change.

### Finding Description
`fund_message` is a signed, permissionless extrinsic that allows any account to top up the relayer fee attached to an existing request or response commitment. It performs two sensitive actions: (1) it transfers `message.amount` from the caller into the `RELAYER_FEE_ACCOUNT` via `T::Currency::transfer`, and (2) it mutates the stored `RequestCommitments`/`ResponseCommitments` metadata to add `message.amount` to `metadata.fee.fee`, persisting the updated fee that later determines relayer compensation during accumulation/delivery. [1](#0-0) 

Unlike other privileged/sensitive calls in the same pallet — e.g. `create_consensus_client`, which explicitly emits `Event::ConsensusClientCreated` after its state change — `fund_message` returns `Ok(())` with no `Self::deposit_event(...)` call at all. [2](#0-1) 

A grep across the codebase confirms there is no `MessageFunded`/`FundMessage` event variant defined or emitted anywhere in `pallet-ismp`, meaning this fee top-up path is entirely invisible to on-chain event consumers.

### Impact Explanation
Relayers, indexers (e.g. `sdk/packages/indexer`), and the Hyperbridge fee-accumulation/withdrawal tooling rely on on-chain events to detect state changes and drive off-chain accounting (as seen in the analogous `RelayerWithdraw` event handling and other indexer event handlers found in the codebase). Because `fund_message` silently increases a request's/response's fee without an event, off-chain relayer software and indexers cannot reactively detect or aggregate these fee top-ups; they would have to poll storage directly to notice the change, rather than being event-driven. This does not itself allow theft or unbacked minting, but it degrades the reliability/observability of the fee/reward accounting subsystem that this campaign's scope explicitly includes ("relayer fee and reward accounting").

### Likelihood Explanation
`fund_message` is callable by any signed account on any pending, non-terminal request/response — it requires no special privilege and can be triggered by a single submitted extrinsic, matching the "unprivileged... relayer... reachable" criterion. Every such call silently updates fee state without a corresponding event, so the missing-event condition is deterministic and always reproducible, not merely theoretical.

### Recommendation
Add and emit a dedicated event (e.g. `Event::MessageFunded { commitment, payer, amount }`) inside `fund_message` immediately after the successful `T::Currency::transfer` and metadata update, for both the `Request` and `Response` commitment branches, so off-chain consumers can track fee top-ups deterministically.

### Proof of Concept
1. Attacker/relayer submits `pallet_ismp::fund_message` with a valid `MessageCommitment::Request(commitment)` pointing to an existing, uncompleted request, and any nonzero `amount`. [3](#0-2) 
2. `T::Currency::transfer` moves `amount` into `RELAYER_FEE_ACCOUNT`, and `metadata.fee.fee += message.amount` is persisted via `RequestCommitments::<T>::insert`. [4](#0-3) 
3. The call returns `Ok(())` with no event deposited — confirmed by grep showing no `MessageFunded`/`FundMessage` event variant exists in the pallet, so no indexer or off-chain relayer subscription can observe this fee increase from chain events alone.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L390-408)
```rust
		/// Emits [`Event::ConsensusClientCreated`] if successful.
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(1, 1))]
		#[pallet::call_index(2)]
		pub fn create_consensus_client(
			origin: OriginFor<T>,
			message: CreateConsensusState,
		) -> DispatchResult {
			T::AdminOrigin::ensure_origin(origin)?;
			let host = Pallet::<T>::default();

			let result = handlers::create_client(&host, message)
				.map_err(|_| Error::<T>::ConsensusClientCreationFailed)?;

			Self::deposit_event(Event::<T>::ConsensusClientCreated {
				consensus_client_id: result.consensus_client_id,
			});

			Ok(())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L439-480)
```rust
		/// Add more funds to a message (request or response) to be used for delivery and execution.
		///
		/// Should not be called on a message that has been completed (delivered or timed-out) as
		/// those funds will be lost forever.
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().writes(5))]
		#[pallet::call_index(4)]
		pub fn fund_message(
			origin: OriginFor<T>,
			message: FundMessageParams<T::Balance>,
		) -> DispatchResult {
			let account = ensure_signed(origin)?;

			let metadata = match message.commitment {
				MessageCommitment::Request(commitment) => RequestCommitments::<T>::get(commitment),
				MessageCommitment::Response(commitment) =>
					ResponseCommitments::<T>::get(commitment),
			};

			let Some(mut metadata) = metadata else {
				return Err(Error::<T>::MessageNotFound.into());
			};

			T::Currency::transfer(
				&account,
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				message.amount,
				Preservation::Expendable,
			)?;

			match message.commitment {
				MessageCommitment::Request(commiment) => {
					metadata.fee.fee += message.amount;
					RequestCommitments::<T>::insert(commiment, metadata);
				},
				MessageCommitment::Response(commiment) => {
					metadata.fee.fee += message.amount;
					ResponseCommitments::<T>::insert(commiment, metadata);
				},
			};

			Ok(())
		}
```
