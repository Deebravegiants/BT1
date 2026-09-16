### Title
`place_bid` in `pallet-intents-coprocessor` lacks `#[transactional]`, allowing a partially-reverted deposit swap to leave an unbacked bid in storage - (File: `modules/pallets/intents-coprocessor/src/lib.rs`)

### Summary
`pallet_intents_coprocessor::Pallet::place_bid` performs multiple sequential storage/currency mutations — `unreserve` the filler's existing deposit, then `reserve` a new deposit, then `Bids::insert` — without the `#[frame_support::transactional]` annotation. If the second mutation (`reserve`) fails after the first (`unreserve`) has already succeeded, the `DispatchError` returned by the call does **not** roll back the already-applied `unreserve`, because in FRAME storage changes are only atomically reverted on an `Err` when the call is explicitly wrapped in a storage transaction. This exactly matches the bug class in the referenced report: "extrinsic with multiple storage mutations isn't annotated with `#[transactional]`."

### Finding Description
`place_bid` is a `Signed` extrinsic, callable by any filler/solver: [1](#0-0) 

The relevant sequence is:
1. `CurrentPhantomOrder`/`Bids` reads and validity checks (no mutation).
2. `if let Some(old_deposit) = Bids::<T>::get(...) { <T as Config>::Currency::unreserve(&filler, old_deposit); }` — **mutation #1**, unconditionally applied and cannot fail.
3. `<T as Config>::Currency::reserve(&filler, deposit).map_err(|_| Error::<T>::InsufficientBalance)?` — **mutation #2**, can fail and return early via `?`.
4. `offchain_index::set(...)` and `Bids::<T>::insert(...)` — only reached on success.

Because the whole call is not wrapped in `#[transactional]` (compare with `pallet-ismp::handle_unsigned`, which *is* annotated: [2](#0-1) ), step 3 failing after step 2 succeeded leaves the chain state as: the filler's previous deposit has already been unreserved (returned to free balance), while `Bids::<T>` still records the *old* deposit amount as if it were still reserved. The stored `Bids` entry is now unbacked by any actually-reserved currency — a genuine storage/accounting corruption caused by the missing transactional boundary, identical in shape to the reported duster/nft bug.

This is reachable by any account that has previously placed a bid and calls `place_bid` again for the same commitment while the effective per-bid deposit (`StorageDepositFee`, governance-adjustable) has increased between the two calls, or more generally whenever the second `reserve` fails for any reason (e.g., the account's free balance was reduced by an unrelated concurrent transaction) after the first `unreserve` succeeded.

### Impact Explanation
The deposit-reservation invariant that the `Bids` storage entry is always backed by an actual `Currency::reserve` is silently violated. Concretely:
- The filler's funds are returned to their free balance early (via the un-reverted `unreserve`) without going through `retract_bid`, while the bid stays visible on-chain/discoverable via `intents_getBidsForOrder` and the `Bids` storage map as if fully deposited.
- A subsequent `retract_bid` on that stale entry unreserves an amount no longer actually reserved (pallet_balances `unreserve` saturates silently rather than erroring), so the pallet emits a `BidRetracted` event with a `refund` amount that was never actually moved — the on-chain deposit accounting no longer reflects the real reserved balance for the account.
- This breaks the deposit-based anti-spam/discoverability guarantee: a filler can retain what appears to be a fully-deposited, discoverable bid while holding zero funds actually locked against it, for as long as it isn't retracted or overwritten by a later successful `place_bid`.

### Likelihood Explanation
Any unprivileged filler can trigger this without governance collusion — the failing `reserve` only requires the filler's free balance to be insufficient for the *new* deposit amount at the moment of a repeat `place_bid` call (e.g., normal fee changes via `set_storage_deposit_fee`, or the filler having spent/reserved balance elsewhere between two of their own `place_bid` calls). No malicious governance action is required, only a natural race between a legitimate fee update or balance change and a filler resubmitting a bid.

### Recommendation
Annotate `place_bid` (and audit `retract_bid` and other multi-mutation calls in this pallet, e.g. `add_deployment`'s loop of `Gateways` mutation + cross-chain dispatch) with `#[frame_support::transactional]` so that a failure in `reserve` after `unreserve` rolls back the entire extrinsic, keeping the `Bids` storage entry and the actual reserved currency amount always consistent.

### Proof of Concept
1. Filler `F` calls `place_bid(commitment, user_op_1)` when `StorageDepositFee = 100`. Result: `F` reserved = 100, `Bids[commitment][F] = 100`.
2. Governance (via `set_storage_deposit_fee`, unrelated to this bug) or another circumstance raises the fee to 150, and `F`'s free balance is less than 150.
3. `F` calls `place_bid(commitment, user_op_2)` again:
   - `Bids::<T>::get` returns `100` → `Currency::unreserve(&F, 100)` executes, `F` reserved becomes 0, free increases by 100.
   - `Currency::reserve(&F, 150)` fails (`InsufficientBalance`), the call returns `Err`.
   - Because there is no `#[transactional]`, the `unreserve` from the previous line remains applied.
4. On-chain state now shows `Bids[commitment][F] = 100` (unchanged, stale) while `F`'s actual reserved balance for this bid is `0` — the deposit backing the bid record no longer exists, demonstrating the storage/currency divergence caused by the missing transactional wrapper. [3](#0-2)

### Citations

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L332-383)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::place_bid())]
		pub fn place_bid(
			origin: OriginFor<T>,
			commitment: H256,
			user_op: BoundedVec<u8, ConstU32<1_048_576>>,
		) -> DispatchResult {
			let filler = ensure_signed(origin)?;

			// Validate user_op is not empty
			ensure!(!user_op.is_empty(), Error::<T>::InvalidUserOp);

			// Phantom orders have stricter rules: one bid per filler, no updates, and only
			// within the configured acceptance window after the order was registered. Every
			// chain's active order is checked, not just the most recently generated one.
			if let Some(active) = CurrentPhantomOrder::<T>::get() {
				if let Some((_, info)) = active.iter().find(|(c, _)| *c == commitment) {
					let window: BlockNumberFor<T> = Self::phantom_bid_window().into();
					ensure!(
						frame_system::Pallet::<T>::block_number() <= info.created_at_block + window,
						Error::<T>::PhantomOrderBidWindowClosed
					);
					ensure!(
						!Bids::<T>::contains_key(&commitment, &filler),
						Error::<T>::DuplicatePhantomBid
					);
				}
			}

			// If a bid already exists, unreserve the old deposit first
			if let Some(old_deposit) = Bids::<T>::get(&commitment, &filler) {
				<T as Config>::Currency::unreserve(&filler, old_deposit);
			}

			let deposit = Self::storage_deposit_fee();

			// Reserve the new deposit
			<T as Config>::Currency::reserve(&filler, deposit)
				.map_err(|_| Error::<T>::InsufficientBalance)?;

			// Store the bid in offchain storage
			let bid = Bid { filler: filler.clone(), user_op: user_op.to_vec() };
			let offchain_key = Self::offchain_bid_key(&commitment, &filler);
			offchain_index::set(&offchain_key, &bid.encode());

			// Store deposit amount in onchain storage for discoverability and accurate refunds
			Bids::<T>::insert(&commitment, &filler, deposit);

			Self::deposit_event(Event::BidPlaced { filler, commitment, deposit });

			Ok(())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L370-382)
```rust
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```
