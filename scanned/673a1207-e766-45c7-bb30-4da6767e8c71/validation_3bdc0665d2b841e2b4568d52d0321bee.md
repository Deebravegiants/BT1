Confirmed: `create_swap` (`substrate/frame/atomic-swap/src/lib.rs:255-280`) accepts an arbitrary `duration: BlockNumberFor<T>` with **no minimum-lock enforcement whatsoever** — unlike the Solidity report's `_validTimelock` 15-minute floor, a caller can even pass `duration = 0`, allowing an immediate `cancel_swap`. Critically, `claim_swap` (lines 297-322) takes the secret `proof: Vec<u8>` in cleartext as a call argument, meaning it becomes publicly visible the moment it is submitted/broadcast — even before finalization, and even if the call ultimately errors out (e.g., because the entry was already removed). This mirrors the Solidity bug's root cause: the two sides of the swap are set up independently, with no cross-chain enforcement that the "target"/counterparty's lock outlives the "source"'s lock.

### Title
Unenforced/asymmetric timelock ordering in `pallet-atomic-swap` allows the counterparty to steal funds by front-running the revealed secret - (File: `substrate/frame/atomic-swap/src/lib.rs`)

### Summary
`pallet-atomic-swap` implements a two-phase HTLC-style cross-chain swap (`create_swap` → `claim_swap`/`cancel_swap`) using a shared `hashed_proof`. Each party independently chooses their own `duration` for their leg of the swap on their own chain, with `create_swap` performing no validation relating the two durations, and no minimum duration at all [1](#0-0) . The pallet's own documentation acknowledges the risk but only as a non-enforced recommendation [2](#0-1) .

### Finding Description
In the intended two-party flow (as shown in the pallet's own test), party A generates a secret `proof`, locks funds on chain1 for B via `create_swap` with `hashed_proof`, and B locks funds on chain2 for A with the same `hashed_proof` [3](#0-2) . A then calls `claim_swap` on chain2 to reveal `proof` in the clear and receive B's funds; B then reuses that now-public `proof` to call `claim_swap` on chain1 [4](#0-3) .

Because `duration` for each leg is chosen independently by each party and unrelated to the other chain's lock [5](#0-4) , B (analogous to the "LP" in the Solidity report) can set an intentionally short `duration` on chain2. If A's `claim_swap` transaction is submitted (and thus the plaintext `proof` becomes visible in the transaction/mempool) before it is finalized, or before A's own timelock has expired, B can:
1. Call `cancel_swap` on chain2 once B's short duration elapses, reclaiming B's own locked funds via `Error::DurationNotPassed` gating only B's own timeline [6](#0-5) .
2. Extract the now-public `proof` value and call `claim_swap` on chain1 before A's (longer) duration passes and before A can `cancel_swap`, since `claim_swap` only checks that `swap.action == action` and that the `hashed_proof` matches — not that B is the original counterparty in any special sense beyond being the recorded `target` [7](#0-6) .

This is the same root-cause pattern as the Solidity finding: the protocol relies on the *revealer* using a strictly shorter lock than the counterparty, but nothing in the code enforces this relationship or a safety margin between the two legs' timelocks — it is only mentioned as a caller responsibility in a doc comment [2](#0-1) . Unlike the Solidity contract, this pallet does not even enforce a minimum floor duration (e.g., 15 minutes) — `duration` can be any `BlockNumberFor<T>` including `0`.

### Impact Explanation
If exploited, the counterparty who reveals second (target of the "shorter"-duration leg) can reclaim their own locked funds via `cancel_swap` and separately steal the other party's funds using the exposed secret, before the honest party's own timelock allows them to `cancel_swap` and recover their assets — resulting in total loss of the honest party's locked balance, analogous to the reported "LP steals user funds" scenario.

### Likelihood Explanation
Exploitation requires only that the victim uses this pallet in the intended cross-chain swap pattern and that the counterparty is adversarial and picks a shorter `duration`/front-runs the revealed proof — no privileged role or trusted party compromise is required, and `create_swap`/`claim_swap`/`cancel_swap` are all reachable by any signed, unprivileged account [8](#0-7) . However, this exact caveat is explicitly documented in the pallet's own doc comments as a known caller responsibility rather than an unknown/silent bug, which affects how it would likely be triaged.

### Recommendation
Consider enforcing a minimum relationship between the swap's `duration` and any config-defined floor (mirroring the Solidity fix of doubling the minimum lock), and/or documenting more prominently — or better, technically enforcing — that a swap's `claim_swap` should not be usable by a party who has already exercised `cancel_swap` on their corresponding leg. At minimum, add a `MinimumDuration` config bound enforced in `create_swap`.

### Proof of Concept
Using the existing test harness pattern in `substrate/frame/atomic-swap/src/tests.rs:65-131`: replicate the two-chain flow, but have "B" call `create_swap` with a very small `duration` (e.g., `1`) instead of `1000`. After block 1, have B call `cancel_swap` to reclaim funds on chain2 before A calls `claim_swap`; then, since A's `claim_swap` call/attempt exposes `proof` in the extrinsic, have B call `claim_swap` on chain1 using that proof to also claim A's funds — demonstrating B receives both their own refunded balance and A's locked balance.

---
**Caveat:** Note that the pallet's doc comment already flags this exact risk as a known design caveat requiring careful `duration` selection by the caller [9](#0-8) , which may mean this would be assessed as expected/documented behavior rather than a novel vulnerability during triage, similar to how the original Solidity report was rated but still fixed by adding an enforced margin.

### Citations

**File:** substrate/frame/atomic-swap/src/lib.rs (L248-252)
```rust
		/// - `hashed_proof`: The blake2_256 hash of the secret proof.
		/// - `balance`: Funds to be sent from origin.
		/// - `duration`: Locked duration of the atomic swap. For safety reasons, it is recommended
		///   that the revealer uses a shorter duration than the counterparty, to prevent the
		///   situation where the revealer reveals the proof too late around the end block.
```

**File:** substrate/frame/atomic-swap/src/lib.rs (L253-352)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(T::DbWeight::get().reads_writes(1, 1).ref_time().saturating_add(40_000_000))]
		pub fn create_swap(
			origin: OriginFor<T>,
			target: T::AccountId,
			hashed_proof: HashedProof,
			action: T::SwapAction,
			duration: BlockNumberFor<T>,
		) -> DispatchResult {
			let source = ensure_signed(origin)?;
			ensure!(
				!PendingSwaps::<T>::contains_key(&target, hashed_proof),
				Error::<T>::AlreadyExist
			);

			action.reserve(&source)?;

			let swap = PendingSwap {
				source,
				action,
				end_block: frame_system::Pallet::<T>::block_number() + duration,
			};
			PendingSwaps::<T>::insert(target.clone(), hashed_proof, swap.clone());

			Self::deposit_event(Event::NewSwap { account: target, proof: hashed_proof, swap });

			Ok(())
		}

		/// Claim an atomic swap.
		///
		/// The dispatch origin for this call must be _Signed_.
		///
		/// - `proof`: Revealed proof of the claim.
		/// - `action`: Action defined in the swap, it must match the entry in blockchain. Otherwise
		///   the operation fails. This is used for weight calculation.
		#[pallet::call_index(1)]
		#[pallet::weight(
			T::DbWeight::get().reads_writes(1, 1)
				.saturating_add(action.weight())
				.ref_time()
				.saturating_add(40_000_000)
				.saturating_add((proof.len() as u64).saturating_mul(100))
		)]
		pub fn claim_swap(
			origin: OriginFor<T>,
			proof: Vec<u8>,
			action: T::SwapAction,
		) -> DispatchResult {
			ensure!(proof.len() <= T::ProofLimit::get() as usize, Error::<T>::ProofTooLarge);

			let target = ensure_signed(origin)?;
			let hashed_proof = blake2_256(&proof);

			let swap =
				PendingSwaps::<T>::get(&target, hashed_proof).ok_or(Error::<T>::InvalidProof)?;
			ensure!(swap.action == action, Error::<T>::ClaimActionMismatch);

			let succeeded = swap.action.claim(&swap.source, &target);

			PendingSwaps::<T>::remove(target.clone(), hashed_proof);

			Self::deposit_event(Event::SwapClaimed {
				account: target,
				proof: hashed_proof,
				success: succeeded,
			});

			Ok(())
		}

		/// Cancel an atomic swap. Only possible after the originally set duration has passed.
		///
		/// The dispatch origin for this call must be _Signed_.
		///
		/// - `target`: Target of the original atomic swap.
		/// - `hashed_proof`: Hashed proof of the original atomic swap.
		#[pallet::call_index(2)]
		#[pallet::weight(T::DbWeight::get().reads_writes(1, 1).ref_time().saturating_add(40_000_000))]
		pub fn cancel_swap(
			origin: OriginFor<T>,
			target: T::AccountId,
			hashed_proof: HashedProof,
		) -> DispatchResult {
			let source = ensure_signed(origin)?;

			let swap = PendingSwaps::<T>::get(&target, hashed_proof).ok_or(Error::<T>::NotExist)?;
			ensure!(swap.source == source, Error::<T>::SourceMismatch);
			ensure!(
				frame_system::Pallet::<T>::block_number() >= swap.end_block,
				Error::<T>::DurationNotPassed,
			);

			swap.action.cancel(&swap.source);
			PendingSwaps::<T>::remove(&target, hashed_proof);

			Self::deposit_event(Event::SwapCancelled { account: target, proof: hashed_proof });

			Ok(())
		}
```

**File:** substrate/frame/atomic-swap/src/tests.rs (L70-103)
```rust
	// A generates a random proof. Keep it secret.
	let proof: [u8; 2] = [4, 2];
	// The hashed proof is the blake2_256 hash of the proof. This is public.
	let hashed_proof = blake2_256(&proof);

	// A creates the swap on chain1.
	chain1.execute_with(|| {
		AtomicSwap::create_swap(
			RuntimeOrigin::signed(A),
			B,
			hashed_proof,
			BalanceSwapAction::new(50),
			1000,
		)
		.unwrap();

		assert_eq!(Balances::free_balance(A), 100 - 50);
		assert_eq!(Balances::free_balance(B), 200);
	});

	// B creates the swap on chain2.
	chain2.execute_with(|| {
		AtomicSwap::create_swap(
			RuntimeOrigin::signed(B),
			A,
			hashed_proof,
			BalanceSwapAction::new(75),
			1000,
		)
		.unwrap();

		assert_eq!(Balances::free_balance(A), 100);
		assert_eq!(Balances::free_balance(B), 200 - 75);
	});
```

**File:** substrate/frame/atomic-swap/src/tests.rs (L105-129)
```rust
	// A reveals the proof and claims the swap on chain2.
	chain2.execute_with(|| {
		AtomicSwap::claim_swap(
			RuntimeOrigin::signed(A),
			proof.to_vec(),
			BalanceSwapAction::new(75),
		)
		.unwrap();

		assert_eq!(Balances::free_balance(A), 100 + 75);
		assert_eq!(Balances::free_balance(B), 200 - 75);
	});

	// B use the revealed proof to claim the swap on chain1.
	chain1.execute_with(|| {
		AtomicSwap::claim_swap(
			RuntimeOrigin::signed(B),
			proof.to_vec(),
			BalanceSwapAction::new(50),
		)
		.unwrap();

		assert_eq!(Balances::free_balance(A), 100 - 50);
		assert_eq!(Balances::free_balance(B), 200 + 50);
	});
```
