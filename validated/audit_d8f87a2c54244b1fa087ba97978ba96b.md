### Title
Front-running `create_swap` with same `(target, hashed_proof)` key allows griefing/DoS - (File: `substrate/frame/atomic-swap/src/lib.rs`)

### Summary
`pallet_atomic_swap::Pallet::create_swap` stores a `PendingSwap` keyed only by `(target, hashed_proof)`, both of which are chosen by the transaction sender and become public as soon as the transaction is broadcast/gossiped (before inclusion in a block). Because the pallet only guards against re-use of an existing key via `ensure!(!PendingSwaps::<T>::contains_key(&target, hashed_proof), Error::<T>::AlreadyExist)` and never binds the call to a specific expected `source`/amount/duration, an attacker who observes a pending `create_swap` extrinsic in the transaction pool can front-run it with an identical `(target, hashed_proof)` pair but a trivial `action` value, causing the legitimate sender's transaction to fail with `AlreadyExist`. This mirrors the Connext `TransactionManager.prepare` griefing report, where an attacker front-runs a call keyed by attacker-independent invariant data but supplies a different `amount`.

### Finding Description
`create_swap` in [1](#0-0)  takes `target`, `hashed_proof`, `action` (which encodes the swap `value`), and `duration` directly from the caller, and only checks that no swap already exists under `(target, hashed_proof)`: [2](#0-1) 

There is no requirement that `msg.sender` (the `source`) match any value known in advance to the intended counterparty, and no uniqueness salt tied to the actual submitter beyond the `hashed_proof` value the *sender* chooses (which becomes visible in the extrinsic itself, before the secret `proof` is ever revealed). The storage key is `(T::AccountId, HashedProof)` as declared in `PendingSwaps` at [3](#0-2) , which is exactly analogous to Connext's `invariantData`-keyed record that excludes attacker-independent fields like `amount`.

Because a transaction's full call data (including `target` and `hashed_proof`) is visible in the transaction pool prior to block inclusion, an attacker can:
1. Observe a pending `create_swap(target=T, hashed_proof=H, action=large_value, duration=D)` from a victim.
2. Submit their own `create_swap(target=T, hashed_proof=H, action=tiny_value, duration=D')` with higher priority/tip so it lands first.
3. The victim's original transaction now fails with `Error::AlreadyExist` [4](#0-3) , wasting the victim's transaction fee and forcing them to restart the whole swap protocol with a new secret/proof.

The attacker can repeat this indefinitely and cheaply for any new swap attempt tied to a given `target`, since the reserved `action` cost can be made arbitrarily small (dust), directly matching the mechanics described in the Connext report.

### Impact Explanation
No funds are stolen directly, but a griefing/denial-of-service condition is created: a legitimate user attempting an atomic swap with a specific counterparty can be perpetually blocked from registering their swap, since the attacker only needs to guess/observe the `(target, hashed_proof)` pair (both fully visible pre-inclusion) and reserve a minimal amount. This wastes the victim's transaction fees and disrupts the intended cross-chain/cross-party swap protocol that this pallet is meant to support.

### Likelihood Explanation
Likelihood is low-to-moderate and requires an attacker actively monitoring the transaction pool and being able to have their transaction included ahead of the victim's (e.g., via higher priority/tip or same-block ordering advantages) — the same precondition acknowledged as "highly unlikely" but still possible by the Connext team in the original report. No privileged role or trusted position is required; any unprivileged account can attempt this.

### Recommendation
Add a mechanism to bind the swap slot to information under the legitimate sender's control that an attacker cannot cheaply replicate to grief, for example:
- Require that the caller of `create_swap` for a given `(target, hashed_proof)` also be recorded, and reject subsequent overwrite attempts only from callers who provide a matching `source` commitment; or
- Include the `source` account (or a per-source nonce/salt) as part of the storage key, so that different senders cannot collide on the same `(target, hashed_proof)` key and block each other; or
- Allow multiple concurrent pending swaps per `(target, hashed_proof)` differentiated by `source`, similar to adding an `initiator`/`msgSender` discriminator as Connext did for `InvariantTransactionData`.

### Proof of Concept
1. Victim broadcasts `create_swap(target = Bob, hashed_proof = H, action = BalanceSwapAction::new(1_000), duration = 1000)` from account `Alice`.
2. Attacker observes this pending extrinsic in the pool (H and Bob are plaintext in the call), and submits `create_swap(target = Bob, hashed_proof = H, action = BalanceSwapAction::new(1), duration = 1000)` from account `Mallory` with a higher priority so it is included first.
3. `PendingSwaps::<T>::insert(Bob, H, swap_with_value_1)` succeeds for Mallory.
4. Alice's transaction is now included and hits `ensure!(!PendingSwaps::<T>::contains_key(&target, hashed_proof), Error::<T>::AlreadyExist)` [5](#0-4)  and fails, reverting Alice's intended swap while costing her the transaction fee. Alice must generate a brand-new `hashed_proof` and retry, and Mallory can repeat the same front-run on the next attempt for a dust cost.

### Citations

**File:** substrate/frame/atomic-swap/src/lib.rs (L197-205)
```rust
	#[pallet::storage]
	pub type PendingSwaps<T: Config> = StorageDoubleMap<
		_,
		Twox64Concat,
		T::AccountId,
		Blake2_128Concat,
		HashedProof,
		PendingSwap<T>,
	>;
```

**File:** substrate/frame/atomic-swap/src/lib.rs (L207-210)
```rust
	#[pallet::error]
	pub enum Error<T> {
		/// Swap already exists.
		AlreadyExist,
```

**File:** substrate/frame/atomic-swap/src/lib.rs (L255-280)
```rust
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
```
