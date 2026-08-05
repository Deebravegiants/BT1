Found a direct analog of the reported vulnerability class in this repo.

### Title
Missing slippage protection (`amount_out_min: None`) in Snowbridge `system-frontend` tip/fee swap enables MEV sandwich attacks - (File: `bridges/snowbridge/pallets/system-frontend/src/lib.rs`)

### Summary
The `pallet-snowbridge-system-frontend` pallet swaps a user-supplied tip/fee asset for Ether via `pallet_asset_conversion`'s `Swap` trait, but explicitly passes `None` for `amount_out_min`, disabling the pallet's built-in slippage protection. This mirrors exactly the reported UniV3Utils issue (`amountOutMinimum: 0`): a swap invoked with no minimum-output guard is exposed to sandwich attacks by MEV actors, resulting in less Ether being obtained than the fair market price would provide.

### Finding Description
`Pallet::swap_and_burn` calls the `Swap::swap_exact_tokens_for_tokens` trait method with a hardcoded `None` and an explicit comment acknowledging the lack of protection: [1](#0-0) 

Unlike normal `pallet_asset_conversion` extrinsics/precompile calls, which require a caller-supplied `amount_out_min` and enforce it via `Error::<T>::ProvidedMinimumNotSufficientForSwap`, this internal caller opts out of that protection entirely by passing `None`: [2](#0-1)  shows the check is skipped whenever `amount_out_min` is `None`.

`swap_and_burn` is reached from `swap_fee_asset_and_burn`, which is invoked by two extrinsics reachable by any signed account:
- `add_tip`, callable directly by `ensure_signed` origin with a caller-chosen tip `Asset`: [3](#0-2) 
- `register_token`, for non-root/non-"here" origins, also triggers the swap with a caller-supplied `fee_asset`: [4](#0-3) 

Since `pallet_asset_conversion` pools are public AMM pools (anyone can add/remove liquidity and swap against them, as seen in the pallet's public `swap_exact_tokens_for_tokens`/`swap_tokens_for_exact_tokens` calls and DEX-style precompile interface: [5](#0-4) ), an attacker can manipulate the pool price around the victim's `add_tip`/`register_token` transaction (front-run to move price against the swap, then back-run to restore it), extracting the difference as MEV profit at the expense of the amount of Ether obtained.

### Impact Explanation
The Ether amount obtained from this unprotected swap (`ether_gained`) directly determines:
- The tip/reward amount relayed to BridgeHub via `AddTip` for `add_tip`, i.e., the actual relayer incentive paid out is reduced: [6](#0-5) 
- The `amount` field forwarded in the `RegisterToken` remote call for `register_token`: [7](#0-6) 

A sandwiched swap silently returns less Ether than the pre-attack market price implies, with no on-chain check to detect or reject it (since `amount_out_min` is `None`). This degrades relayer tips and potentially registration fees paid to the bridge, without reverting the transaction — the caller's assets are consumed and burned for teleport regardless of how bad the swap execution was.

### Likelihood Explanation
Any unprivileged, signed account can call `add_tip` with an arbitrary tip `Asset`/amount, and the underlying `pallet_asset_conversion` pools are open, permissionless AMMs that any party can also trade against. This gives an MEV actor (or a malicious/opportunistic block author/searcher) a straightforward, low-cost, repeatable griefing/extraction vector whenever the swapped asset's pool has manipulable depth relative to gas costs — analogous to the original report's observation that this is most exploitable on low-gas-cost chains.

### Recommendation
Compute an off-chain/at-call-time minimum acceptable output (e.g., via `AssetConversionApi::quote_price_exact_tokens_for_tokens` with an acceptable slippage tolerance) and pass it as `Some(amount_out_min)` to `Swap::swap_exact_tokens_for_tokens` in `swap_and_burn`, rather than `None`. Alternatively, expose a slippage/minimum-out parameter on the `add_tip`/`register_token` extrinsics so callers can bound their own exposure, and revert the swap (propagating the error) if the minimum is not met.

### Proof of Concept
1. Attacker observes a pending `add_tip(message_id, asset)` (or `register_token`) transaction in the transaction pool where `asset` ≠ Ether and the `pallet_asset_conversion` pool for `asset → Ether` has limited liquidity.
2. Attacker front-runs with a large swap that shifts the pool price unfavorably for the pending swap (buying up Ether / selling the tip asset into the pool), using the pallet's public `swap_tokens_for_exact_tokens`/`swap_exact_tokens_for_tokens` extrinsics.
3. Victim's transaction executes `swap_and_burn`, which calls `Swap::swap_exact_tokens_for_tokens(..., amount_out_min: None, ...)` — since no minimum is enforced, the swap succeeds at the now-degraded price, producing less `ether_gained` than intended.
4. Attacker back-runs, reversing their initial swap to restore the pool price and capture the difference as profit.
5. Result: the relayer tip forwarded via `AddTip` (or the registration `amount`) is smaller than it should be, and the victim/protocol has no recourse since the extrinsic did not revert.

### Citations

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L225-252)
```rust
		pub fn register_token(
			origin: OriginFor<T>,
			asset_id: Box<VersionedLocation>,
			metadata: AssetMetadata,
			fee_asset: Asset,
		) -> DispatchResult {
			ensure!(!Self::export_operating_mode().is_halted(), Error::<T>::Halted);

			let asset_location: Location =
				(*asset_id).try_into().map_err(|_| Error::<T>::UnsupportedLocationVersion)?;
			let origin_location = T::RegisterTokenOrigin::ensure_origin(origin, &asset_location)?;

			let ether_gained = if origin_location.is_here() {
				// Root origin/location does not pay any fees/tip.
				0
			} else {
				Self::swap_fee_asset_and_burn(origin_location.clone(), fee_asset)?
			};

			let call = Self::build_register_token_call(
				origin_location.clone(),
				asset_location,
				metadata,
				ether_gained,
			)?;

			Self::send_transact_call(origin_location, call)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L254-273)
```rust
		/// Add an additional relayer tip for a committed message identified by `message_id`.
		/// The tip asset will be swapped for ether.
		#[pallet::call_index(2)]
		#[pallet::weight(
			T::WeightInfo::add_tip()
				.saturating_add(T::BackendWeightInfo::transact_add_tip())
		)]
		pub fn add_tip(origin: OriginFor<T>, message_id: MessageId, asset: Asset) -> DispatchResult
		where
			<T as frame_system::Config>::AccountId: Into<Location>,
		{
			let who = ensure_signed(origin)?;

			let ether_gained = Self::swap_fee_asset_and_burn(who.clone().into(), asset)?;

			// Send the tip details to BH to be allocated to the reward in the Inbound/Outbound
			// pallet
			let call = Self::build_add_tip_call(who.clone(), message_id.clone(), ether_gained);
			Self::send_transact_call(who.into(), call)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L290-317)
```rust
		fn swap_and_burn(
			origin: Location,
			tip_asset_location: Location,
			ether_location: Location,
			tip_amount: u128,
		) -> Result<u128, DispatchError> {
			// Swap tip asset to ether
			let swap_path = vec![tip_asset_location.clone(), ether_location.clone()];
			let who = T::AccountIdConverter::convert_location(&origin)
				.ok_or(Error::<T>::LocationConversionFailed)?;

			let ether_gained = T::Swap::swap_exact_tokens_for_tokens(
				who.clone(),
				swap_path,
				tip_amount,
				None, // No minimum amount required
				who,
				true,
			)?;

			// Burn the ether
			let ether_asset = Asset::from((ether_location.clone(), ether_gained));

			burn_for_teleport::<T::AssetTransactor>(&origin, &ether_asset)
				.map_err(|_| Error::<T>::BurnError)?;

			Ok(ether_gained)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L319-338)
```rust
		// Build the call to dispatch the `EthereumSystem::register_token` extrinsic on BH
		fn build_register_token_call(
			sender: Location,
			asset: Location,
			metadata: AssetMetadata,
			amount: u128,
		) -> Result<BridgeHubRuntime<T>, Error<T>> {
			// reanchor locations relative to BH
			let sender = Self::reanchored(sender)?;
			let asset = Self::reanchored(asset)?;

			let call = BridgeHubRuntime::EthereumSystem(EthereumSystemCall::RegisterToken {
				sender: Box::new(VersionedLocation::from(sender)),
				asset_id: Box::new(VersionedLocation::from(asset)),
				metadata,
				amount,
			});

			Ok(call)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L340-351)
```rust
		// Build the call to dispatch the `EthereumSystem::add_tip` extrinsic on BH
		fn build_add_tip_call(
			sender: AccountIdOf<T>,
			message_id: MessageId,
			amount: u128,
		) -> BridgeHubRuntime<T> {
			BridgeHubRuntime::EthereumSystem(EthereumSystemCall::AddTip {
				sender,
				message_id,
				amount,
			})
		}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L988-1002)
```rust
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
```

**File:** substrate/frame/asset-conversion/precompiles/src/lib.rs (L56-85)
```rust
	interface IAssetConversion {
		/// Swap an exact amount of input tokens for as many output tokens as possible.
		/// @param path Ordered list of SCALE-encoded asset identifiers defining the swap route.
		/// @param amountIn Exact amount of the first asset to swap.
		/// @param amountOutMin Minimum acceptable amount of the last asset to receive.
		/// @param sendTo Address to receive the output tokens.
		/// @param keepAlive If true, ensures the sender account stays above existential deposit.
		/// @return amountOut The amount of output tokens received.
		function swapExactTokensForTokens(
			bytes[] calldata path,
			uint256 amountIn,
			uint256 amountOutMin,
			address sendTo,
			bool keepAlive
		) external returns (uint256 amountOut);

		/// Swap tokens to receive an exact amount of output tokens.
		/// @param path Ordered list of SCALE-encoded asset identifiers defining the swap route.
		/// @param amountOut Exact amount of the last asset to receive.
		/// @param amountInMax Maximum acceptable amount of the first asset to spend.
		/// @param sendTo Address to receive the output tokens.
		/// @param keepAlive If true, ensures the sender account stays above existential deposit.
		/// @return amountIn The amount of input tokens spent.
		function swapTokensForExactTokens(
			bytes[] calldata path,
			uint256 amountOut,
			uint256 amountInMax,
			address sendTo,
			bool keepAlive
		) external returns (uint256 amountIn);
```
