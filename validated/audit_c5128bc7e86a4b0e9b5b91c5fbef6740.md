### Title
Cross-chain token amount conversion in `pallet-hyper-fungible-token` trusts a snapshot decimal invariant that is never re-validated, allowing an unbacked mint on the destination chain - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s `send` extrinsic scales a locally-escrowed/burned amount into the destination chain's ERC20 representation using `convert_to_erc20(value, erc_decimals, local_decimals)`, where `local_decimals` is read live from the asset's `pallet-assets` metadata and `erc_decimals` is a value recorded once, at registration time, in the `Precisions` storage map. The only place the relationship `erc_decimals >= local_decimals` is enforced is at `register_token`/`update_token` time; it is never re-checked when the asset's metadata decimals are later changed. This is the same bug class as the referenced report: two values (`long`/`short` payoff type there, `erc_decimals`/`local_decimals` here) are assumed to stay consistent, but only a partial/one-time check enforces that relationship, and drift between them silently breaks a core invariant used elsewhere in the protocol.

### Finding Description
- At registration, the pallet enforces `config.decimals >= local_decimals` (i.e. `erc_decimals >= local_decimals`) before storing `Precisions::<T>::insert(local_id, chain, config.decimals)`: [1](#0-0) 

- `local_decimals` for non-native assets is *not* a fixed value captured at registration — it is re-read from `pallet-assets` metadata every time `send` or `on_accept` executes: [2](#0-1) 

- The scaling math assumes `erc_decimals >= local_decimals` and uses `saturating_sub`, which silently clamps to zero (i.e. applies *no* scaling) instead of erroring when that assumption is violated: [3](#0-2) 

- `pallet-assets`' `set_metadata` (decimals field) is callable at any time by the asset's registered team/owner — it is not locked once the asset is registered with `pallet-hyper-fungible-token`. An attacker who controls a registered asset's metadata (e.g. the creator of a permissionless custom asset that was later registered via `register_token`, satisfying `erc_decimals >= local_decimals` at that point in time) can later call `set_metadata` to raise `local_decimals` above the already-recorded `erc_decimals`.
- Once `local_decimals > erc_decimals`, `erc_decimals.saturating_sub(local_decimals)` clamps to `0` inside `convert_to_erc20`, so `send()` stops applying the down-scaling multiplier that should shrink the raw value into the EVM token's smaller decimal precision. The resulting `erc20_amount` dispatched in the `Send` message is therefore inflated by a factor of `10^(local_decimals - erc_decimals)` relative to the true value of what was actually escrowed/burned locally.
- The destination `HyperFungibleToken`/`WrappedHyperFungibleToken` EVM contract has no way to detect this — it simply mints/releases the amount encoded in the message. The result is an unbacked mint of value on the destination chain relative to what was actually locked/burned on the source chain.

### Impact Explanation
This produces a genuine value-creation ("unbacked mint") bug: the amount credited on the destination EVM chain no longer corresponds to the amount escrowed or burned on the source substrate chain. An attacker who triggers this can extract more value on the destination chain than they gave up on the source chain, directly draining the pallet's escrow custody (for native assets) or minting excess wrapped supply (for non-native assets) relative to backing — a High severity, concrete theft/inflation impact reachable through the pallet's own unprivileged `send` extrinsic.

### Likelihood Explanation
The precondition — retaining control of an asset's `pallet-assets` metadata after that asset has been registered with `pallet-hyper-fungible-token` — is the normal, expected state for any asset whose creator/team still holds the metadata-update permission (e.g. a permissionlessly-created custom asset that governance later approved for cross-chain use via `register_token`). No `CreateOrigin`/governance misbehavior is required after registration; the attacker only needs an ordinary `set_metadata` call followed by an ordinary `send` call, both of which are standard, expected operations exposed to unprivileged/asset-owner accounts.

### Recommendation
Do not rely on a one-time registration-time check for an invariant (`erc_decimals >= local_decimals`) that depends on mutable state (`pallet-assets` metadata decimals). Either:
- Snapshot and freeze the local asset's decimals at registration time instead of reading them live, or
- Re-validate `erc_decimals >= local_decimals` on every `send`/`on_accept` call and reject the transfer (rather than silently clamping via `saturating_sub`) if the invariant no longer holds, or
- Lock/disallow further `set_metadata` decimal changes for any asset once it is registered with `pallet-hyper-fungible-token`.

### Proof of Concept
1. Attacker creates a custom asset `A` in `pallet-assets` with `decimals = 6` and retains the team/owner role.
2. Governance (`CreateOrigin`) calls `register_token` for asset `A` with `chains = { EVM(dest): { token_contract, decimals: 18 } }`. This passes the `ensure!(config.decimals >= local_decimals, ErcDecimalsBelowLocal)` check (18 ≥ 6) and stores `Precisions[A][dest] = 18`. [4](#0-3) 
3. Attacker calls `pallet_assets::set_metadata(A, name, symbol, decimals=20)` — a routine, unprivileged-to-Hyperbridge-governance call available to the asset's own team.
4. Attacker calls `send(params { asset_id: A, destination: dest, amount: X, ... })`.
   - `erc_decimals = Precisions::get(A, dest) = 18` (unchanged).
   - `decimals = fungibles::metadata::Inspect::decimals(A) = 20` (now higher).
   - `convert_to_erc20(X, 18, 20)` computes `erc_decimals.saturating_sub(local_decimals) = 0`, so `erc20_amount = X` unscaled, instead of the correct `X / 10^2`. [5](#0-4) 
5. The `Send` message dispatched to the EVM `HyperFungibleToken` contract carries `erc20_amount = X` (100× too large relative to what was actually burned/escrowed for a 20-vs-18 decimal drift), causing the destination contract to mint/release far more value than was locked on the source chain.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L267-290)
```rust
			} else {
				let is_native = NativeAssets::<T>::get(params.asset_id.clone());
				if is_native {
					<T as Config>::Assets::transfer(
						params.asset_id.clone(),
						&who,
						&Self::pallet_account(),
						params.amount.into(),
						Preservation::Expendable,
					)?;
				} else {
					<T as Config>::Assets::burn_from(
						params.asset_id.clone(),
						&who,
						params.amount.into(),
						Preservation::Expendable,
						Precision::Exact,
						Fortitude::Polite,
					)?;
				}
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					params.asset_id.clone(),
				)
			};
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L327-368)
```rust
		/// Registers a new token with per-chain contract configuration
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::register_token(registration.chains.len() as u32))]
		pub fn register_token(
			origin: OriginFor<T>,
			registration: TokenRegistration<AssetId<T>>,
		) -> DispatchResult {
			T::CreateOrigin::ensure_origin(origin)?;

			let local_decimals = if registration.local_id == T::NativeAssetId::get() {
				T::Decimals::get()
			} else {
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					registration.local_id.clone(),
				)
			};

			NativeAssets::<T>::insert(registration.local_id.clone(), registration.native);

			let chains: Vec<StateMachine> = registration.chains.keys().cloned().collect();
			for (chain, config) in registration.chains {
				// This pallet bridges substrate <-> EVM only; reject non-EVM peers.
				if !matches!(chain, StateMachine::Evm(_)) {
					return Err(Error::<T>::NonEvmPeerChain.into());
				}
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
				let token_contract = config.token_contract.0.to_vec();
				TokenContracts::<T>::insert(
					chain,
					registration.local_id.clone(),
					token_contract.clone(),
				);
				ContractToAsset::<T>::insert(
					chain,
					token_contract,
					registration.local_id.clone(),
				);
				Precisions::<T>::insert(registration.local_id.clone(), chain, config.decimals);
			}
```

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L39-59)
```rust
/// Converts an ERC20 U256 amount to a local balance type
///
/// Divides by 10^(erc_decimals - local_decimals) to scale down from ERC20 precision.
/// The target type must implement `FromStr`.
pub fn convert_to_balance<B: core::str::FromStr>(
	value: U256,
	erc_decimals: u8,
	local_decimals: u8,
) -> Result<B, B::Err> {
	let dec_str = (value /
		U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32)))
	.to_string();
	dec_str.parse::<B>()
}

/// Converts a local u128 balance to an ERC20 U256 amount
///
/// Multiplies by 10^(erc_decimals - local_decimals) to scale up to ERC20 precision
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```
