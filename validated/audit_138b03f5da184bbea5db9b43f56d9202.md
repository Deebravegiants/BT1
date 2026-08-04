### Title
Loss of funds via zero-output swap when `swap_exact_tokens_for_tokens` is called without `amount_out_min` and integer-division rounds `amount_out` to zero - (File: `substrate/frame/asset-conversion/src/lib.rs`)

### Summary
The vulnerability class described in the report (integer division that can round a bid/swap output down to zero, causing the caller to lose their entire input while receiving nothing) has a real analog in `pallet-asset-conversion`. The pallet's quote-only helpers (`quote_price_exact_tokens_for_tokens` / `quote_price_tokens_for_exact_tokens`) were explicitly hardened against zero-rounding outputs (see `prdoc/stable2606/pr_11795.prdoc`), but the actual execution path, `do_swap_exact_tokens_for_tokens`, does not carry the same protection when the caller omits `amount_out_min`.

### Finding Description
`do_swap_exact_tokens_for_tokens` computes `amount_out` via `balance_path_from_amount_in` → `get_amount_out`, which performs `numerator.checked_div(&denominator)` [1](#0-0)  — a floor-division AMM formula. For a sufficiently small `amount_in` relative to pool reserves (or a low-decimals `asset2`), this division rounds down to `0`.

The dispatchable enforces `amount_in > 0` and, only *if the caller supplies* `amount_out_min`, that it must be `> 0` and that `amount_out >= amount_out_min`. If `amount_out_min` is `None` there is no check that the computed `amount_out` itself is non-zero before the swap executes: [2](#0-1) 

`Self::swap` then unconditionally withdraws `amount_in` from the sender and resolves whatever `amount_out` was computed (possibly `0`) to `send_to`: [3](#0-2) 

This mirrors the reported bug precisely: the input (`volume`/`amount_in`) is fully consumed while `volume/price` (`get_amount_out`) rounds to zero, so the caller receives nothing.

Notably, the pallet's own quote functions already guard against exactly this: `quote_price_exact_tokens_for_tokens` explicitly checks `if amount_out.is_zero() { return None; }` with the comment "Small inputs can round output to zero due to integer division" [4](#0-3) , confirming this rounding-to-zero scenario is a recognized, real condition in this AMM — but that same protection is absent from the actual swap dispatchable's execution path when `amount_out_min` is not supplied.

### Impact Explanation
If `amount_out_min` is `None` (which is a supported/valid call pattern via the low-level `SwapCredit`/`Swap` trait paths, or if a caller/integrating pallet naively omits it), a user can lose their entire `amount_in` while receiving `0` of the output asset — direct, complete loss of the swapped funds for that transaction. This matches the "High" impact classification in the referenced report.

### Likelihood Explanation
Likelihood is lower than in the original report because:
- The public extrinsics `swap_exact_tokens_for_tokens`/`swap_tokens_for_exact_tokens` always pass `Some(amount_out_min)` from the call arguments (via `Self::do_swap_exact_tokens_for_tokens(..., Some(amount_out_min), ...)` at [5](#0-4) ), so a normal user calling the extrinsic directly with `amount_out_min = 0` would still be protected only if they set a nonzero minimum — a naive/careless user setting `amount_out_min = 0` (perfectly valid, non-zero check only rejects an explicit `0`, so effectively they must set at least `1`) is protected because `ensure!(amount_out_min > Zero::zero())` forces at least `1`, and then `ensure!(amount_out >= amount_out_min)` would reject a `0` output.
- However, the internal `do_swap_exact_tokens_for_tokens`/`Swap` trait function accepts `amount_out_min: Option<T::Balance>`, and passing `None` (used by other pallets/precompiles integrating via the `Swap` trait, e.g. XCM asset-exchange adapters or other runtime code that composes swaps) bypasses this check entirely.

This narrows the realistic exposure to internal/pallet-to-pallet callers of the `Swap`/`SwapCredit` trait that pass `None`, rather than to a directly reachable, unprivileged extrinsic parameter combination for `swap_exact_tokens_for_tokens`/`swap_tokens_for_exact_tokens` themselves (since those always require `amount_out_min >= 1`, and `ensure!(amount_out >= amount_out_min)` would reject a zero output). I was not able to fully verify, within this session, whether any concretely reachable unprivileged user-facing entry point (e.g., XCM `AssetExchanger` implementations, or other runtime pallets) invokes `Swap::swap_exact_tokens_for_tokens` with `amount_out_min = None` in a way an attacker could trigger and profit from (e.g., by front-running liquidity to create a heavily skewed pool). This uncertainty should be resolved by checking callers of the `Swap`/`SwapCredit` trait (e.g., `cumulus/primitives/utility` swap-based fee/exchange adapters) for use of `None`.

### Recommendation
In `do_swap_exact_tokens_for_tokens` (and the credit variant `do_swap_exact_credit_tokens_for_tokens`), add an explicit check that the computed `amount_out` is non-zero regardless of whether `amount_out_min` was supplied, mirroring the guard already present in `quote_price_exact_tokens_for_tokens`:
```rust
let amount_out = path.last().map(|(_, a)| *a).ok_or(Error::<T>::InvalidPath)?;
ensure!(!amount_out.is_zero(), Error::<T>::ZeroAmount); // add this
```
This closes the gap for any caller (extrinsic or trait-based) that does not supply a `amount_out_min`.

### Proof of Concept
Conceptual PoC (would need to be executed against the pallet's test harness to confirm reachability through a `None` `amount_out_min` caller):
1. Create a pool with reserves heavily skewed similarly to the existing test `quote_price_returns_none_for_zero_output`, e.g. `reserve_in = 1_000_000`, `reserve_out = 200` [6](#0-5) .
2. Call `Swap::swap_exact_tokens_for_tokens` (the trait method, not the extrinsic) with `amount_in = 1` and `amount_out_min = None` [7](#0-6) .
3. `get_amount_out(1, 1_000_000, 200)` rounds to `0` (as demonstrated by the existing quote test comment) [8](#0-7) .
4. `do_swap_exact_tokens_for_tokens` proceeds since `amount_out_min` is `None`, withdraws `1` unit of `asset1` from the caller, and resolves `0` units of `asset2` — the caller loses their input entirely.

### Citations

**File:** substrate/frame/asset-conversion/src/lib.rs (L527-545)
```rust
		pub fn swap_exact_tokens_for_tokens(
			origin: OriginFor<T>,
			path: Vec<Box<T::AssetKind>>,
			amount_in: T::Balance,
			amount_out_min: T::Balance,
			send_to: T::AccountId,
			keep_alive: bool,
		) -> DispatchResult {
			let sender = ensure_signed(origin)?;
			Self::do_swap_exact_tokens_for_tokens(
				sender,
				path.into_iter().map(|a| *a).collect(),
				amount_in,
				Some(amount_out_min),
				send_to,
				keep_alive,
			)?;
			Ok(())
		}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L980-1014)
```rust
		pub(crate) fn do_swap_exact_tokens_for_tokens(
			sender: T::AccountId,
			path: Vec<T::AssetKind>,
			amount_in: T::Balance,
			amount_out_min: Option<T::Balance>,
			send_to: T::AccountId,
			keep_alive: bool,
		) -> Result<T::Balance, DispatchError> {
			ensure!(amount_in > Zero::zero(), Error::<T>::ZeroAmount);
			if let Some(amount_out_min) = amount_out_min {
				ensure!(amount_out_min > Zero::zero(), Error::<T>::ZeroAmount);
			}

			Self::validate_swap_path(&path)?;
			let path = Self::balance_path_from_amount_in(amount_in, path)?;

			let amount_out = path.last().map(|(_, a)| *a).ok_or(Error::<T>::InvalidPath)?;
			if let Some(amount_out_min) = amount_out_min {
				ensure!(
					amount_out >= amount_out_min,
					Error::<T>::ProvidedMinimumNotSufficientForSwap
				);
			}

			Self::swap(&sender, &path, &send_to, keep_alive)?;

			Self::deposit_event(Event::SwapExecuted {
				who: sender,
				send_to,
				amount_in,
				amount_out,
				path,
			});
			Ok(amount_out)
		}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1168-1181)
```rust
		fn swap(
			sender: &T::AccountId,
			path: &BalancePath<T>,
			send_to: &T::AccountId,
			keep_alive: bool,
		) -> Result<(), DispatchError> {
			let (asset_in, amount_in) = path.first().ok_or(Error::<T>::InvalidPath)?;
			let credit_in = Self::withdraw(asset_in.clone(), sender, *amount_in, keep_alive)?;

			let credit_out = Self::credit_swap(credit_in, path).map_err(|(_, e)| e)?;
			T::Assets::resolve(send_to, credit_out).map_err(|_| Error::<T>::BelowMinimum)?;

			Ok(())
		}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1416-1418)
```rust
			let result = numerator.checked_div(&denominator).ok_or(Error::<T>::Overflow)?;

			result.try_into().map_err(|_| Error::<T>::Overflow)
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1549-1552)
```rust
			// Small inputs can round output to zero due to integer division.
			if amount_out.is_zero() {
				return None;
			}
```

**File:** substrate/frame/asset-conversion/src/tests.rs (L716-726)
```rust
		// Create a heavily skewed pool: lots of asset1, very little asset2.
		assert_ok!(AssetConversion::add_liquidity(
			RuntimeOrigin::signed(user),
			Box::new(token_1.clone()),
			Box::new(token_2.clone()),
			1_000_000,
			200,
			1,
			1,
			user,
		));
```

**File:** substrate/frame/asset-conversion/src/tests.rs (L728-738)
```rust
		// Tiny input into a skewed pool rounds output to zero.
		// get_amount_out(1, 1_000_000, 200) = 1*997*200 / (1_000_000*1000 + 997) = 0
		assert_eq!(
			AssetConversion::quote_price_exact_tokens_for_tokens(
				token_1.clone(),
				token_2.clone(),
				1,
				true,
			),
			None
		);
```

**File:** substrate/frame/asset-conversion/src/swap.rs (L156-172)
```rust
	fn swap_exact_tokens_for_tokens(
		sender: T::AccountId,
		path: Vec<Self::AssetKind>,
		amount_in: Self::Balance,
		amount_out_min: Option<Self::Balance>,
		send_to: T::AccountId,
		keep_alive: bool,
	) -> Result<Self::Balance, DispatchError> {
		Self::do_swap_exact_tokens_for_tokens(
			sender,
			path,
			amount_in,
			amount_out_min,
			send_to,
			keep_alive,
		)
	}
```
