## Title
Unbounded `decimals` in `register_token` allows precision-scaling arithmetic to overflow, permanently bricking a token's `send` and `on_accept` routes - (File: `modules/pallets/hyper-fungible-token/src/lib.rs`, `modules/pallets/hyper-fungible-token/src/impls.rs`)

## Summary
`pallet-hyper-fungible-token::register_token` only checks that the EVM-side `decimals` value is `>= local_decimals`; it does not bound how large that value may be relative to the local asset's decimals. That difference feeds directly into `10u128.pow(erc_decimals - local_decimals)` inside `convert_to_erc20`/`convert_to_balance`, which is used by the unprivileged `send` extrinsic (source side) and by `on_accept` (destination side, invoked for every incoming ISMP `PostRequest` from the paired EVM contract). A single privileged parameter typo (analogous to the Singularity Finance fee-tier misconfiguration) silently plants a landmine that any ordinary user detonates on their next transfer.

## Finding Description
`register_token` validates the decimal precision configured for a chain like this: [1](#0-0) 

The only guard is `ensure!(config.decimals >= local_decimals, Error::<T>::ErcDecimalsBelowLocal)` — there is no upper bound on `config.decimals` itself, nor on the gap `config.decimals - local_decimals`.

That value is later used unconditionally in the scaling helpers: [2](#0-1) 

`10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32)` overflows `u128` once the exponent reaches 39 (10^39 > u128::MAX ≈ 3.4×10^38). Both `send` (unprivileged, signed-origin extrinsic) and `on_accept` (triggered by any relayed `PostRequest` from the registered EVM contract) call this scaling path unconditionally on every transfer for that asset: [3](#0-2) [4](#0-3) 

This is a direct structural analog of the reported incident: a privileged parameter (Uniswap fee tier / here, `decimals`) is accepted with no bound/sanity check, sits dormant, and is then unconditionally consumed on a normal, unprivileged user action (vault deposit/redeem there; `send`/`on_accept` here), turning a configuration slip into an on-chain fault reachable by anyone.

## Impact Explanation
Once such a token is registered with an excessive `decimals` gap (e.g. local asset at 0–2 decimals, EVM side mistakenly set anywhere near 40+), every subsequent `send` for that asset panics/overflows on `10u128.pow(...)`, and every incoming `on_accept` PostRequest for that asset from the counterpart EVM contract also fails identically. This permanently freezes that asset's cross-chain route in both directions — no user can move it out, and inbound transfers for the same asset cannot be delivered (`on_accept` failing means relayed requests cannot be processed, matching the "route unable to deliver messages" acceptance criterion). Any user's ordinary transfer is what triggers the fault, not a special exploit — the harm is caused by an unprivileged transaction reaching unvalidated privileged state.

## Likelihood Explanation
This is Medium likelihood: it requires the `CreateOrigin` to register a token with a badly mis-set `decimals` value (same class of unforced parameter error as the reported incident's fee-tier typo), which is plausible for permissionless/governance-lite deployments of this pallet (its own docs mark it as a general-purpose SDK-style pallet, not hardened for arbitrary chain configuration). No malicious governance action is required — only a data-entry error, exactly like the "unsupported Uniswap V3 fee tier of 42" mistake in the analog report. After that, exploitation-by-normal-use is guaranteed and requires no attacker skill.

## Recommendation
- Enforce an explicit maximum bound on `config.decimals` (and on `config.decimals - local_decimals`), e.g. cap the difference such that `10^(diff)` cannot exceed `u128::MAX` (diff ≤ 38), in both `register_token` and `update_token`.
- Replace `10u128.pow(...)` with a `checked_pow`/`checked_mul` path in `convert_to_erc20`/`convert_to_balance` that returns a proper `DispatchError` instead of overflowing, so a misconfiguration fails safely rather than bricking the asset's route.
- Add a regression test registering a token with a large decimals gap and asserting `register_token` rejects it, plus a test asserting `send`/`on_accept` return a graceful error instead of panicking if such a misconfiguration ever exists in storage.

## Proof of Concept
1. `CreateOrigin` calls `register_token` for an asset whose local decimals are e.g. `0`, and supplies `ChainConfig { token_contract, decimals: 45 }` for `StateMachine::Evm(x)` — this passes the only check (`45 >= 0`).
2. Any signed user calls `send` for that asset/destination pair.
3. Inside `send`, `convert_to_erc20(amount, 45, 0)` computes `10u128.pow(45)`, which overflows `u128` — panicking (if overflow-checks are enabled at the runtime build level, which could not be conclusively verified in this review since no `overflow-checks` setting was found in the repo, defaulting to whatever the polkadot-sdk build profile uses) or silently wrapping to an incorrect value.
4. Symmetrically, any incoming `PostRequest` from the paired EVM contract for this asset hits the identical scaling call in `on_accept`, so inbound delivery for the asset is likewise broken.

Note: I was unable to confirm from the indexed files whether the workspace's build profile sets `overflow-checks = true` (no matching Cargo profile settings were found in the index), so I cannot definitively state whether the failure mode is a panic (halting block execution) or a silent wraparound (producing a wrong minted/burned amount). Either outcome satisfies the "route unable to deliver messages" / "unsound state" acceptance criteria, but the exact mechanism should be confirmed by a Devin session with full repository and build-profile access.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-296)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L336-368)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L82-91)
```rust
		let erc_decimals = Precisions::<T>::get(local_asset_id.clone(), source)
			.ok_or(HftError::DecimalsNotConfigured(source))?;
		let amount = convert_to_balance::<
			<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance,
		>(
			U256::from_big_endian(&message.amount.to_be_bytes::<32>()),
			erc_decimals,
			decimals,
		)
		.map_err(|e| HftError::InvalidAmountConversion(format!("{e:?}")))?;
```
