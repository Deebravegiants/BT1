### Title
Cross-chain token transfers to lower-decimal assets silently round to zero, permanently burning user funds - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s `convert_to_balance` performs a floor division when converting an incoming ERC-20 amount (18 decimals on the EVM side) down to the local asset's decimals. Any transfer whose amount is smaller than `10^(erc_decimals - local_decimals)` raw units is burned in full on the source `HyperFungibleToken` contract but mints `0` on the destination substrate chain, with no revert and no refund path — an exact analog of the reported "tokens with decimals less than 18 are not supported" rounding bug.

### Finding Description
On the EVM side, `HyperFungibleToken.send()` burns `params.amount` verbatim and dispatches it unscaled in the ISMP message body, since the contract's `decimals()` is always the inherited OZ default of 18: [1](#0-0) 

On the substrate side, `on_accept` converts this raw 18-decimal amount down to the local asset's decimals via `convert_to_balance`, using `erc_decimals` recorded in `Precisions` (set by the admin at `register_token`/`update_token`) and the local asset's actual decimals: [2](#0-1) 

`convert_to_balance` performs a plain integer (floor) division:
```rust
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
``` [3](#0-2) 

The pallet enforces `config.decimals >= local_decimals` at registration time, so `erc_decimals - local_decimals` is always a valid, non-negative exponent — but it can be large (e.g. `18 - 6 = 12` for a local asset with 6 decimals, which is exactly the enforced/expected configuration for low-decimal assets): [4](#0-3) 

Because the division floors, any `value < 10^(erc_decimals - local_decimals)` (e.g. any EVM-side amount below `1e12` wei when the local asset has 6 decimals — up to `0.000001` full tokens) converts to a local balance of `0`. The user's tokens are already burned on the EVM contract (`_burn(msg.sender, params.amount)` executed before dispatch) and the ISMP message is delivered successfully (`onAccept`/`on_accept` complete without error, so this is not a timeout that would trigger the refund path in `on_timeout`). The mint call `Assets::mint_into(local_asset_id, &beneficiary, 0)` (or the native transfer of `0`) succeeds silently, and the funds are unrecoverable.

The same floor-division logic and `Precisions`-derived decimals are also used in `on_timeout`'s refund path, meaning even a timed-out transfer's refund amount is subject to the same truncation: [5](#0-4) 

### Impact Explanation
This is a permanent, unrecoverable loss of user funds reachable by any unprivileged token bridger simply calling `HyperFungibleToken.send()` with an amount whose value, once converted to the destination asset's lower decimal precision, floors to zero. No revert occurs anywhere in the pipeline — the EVM burn succeeds, the ISMP message delivers successfully, and the substrate-side mint of `0` also succeeds, so there is no error signal to the user and no automatic remediation (a timeout-triggered refund is the only recovery mechanism, and it does not fire on a successful delivery). Given that low-decimal local assets (6 decimals is common, e.g. USDC-style assets) are explicitly supported and even mandated to configure `erc_decimals (18) >= local_decimals`, this is a realistic, not a contrived, configuration.

### Likelihood Explanation
Any registered non-native asset with local decimals below the EVM side's 18 decimals is affected. A user (or an integrator's dApp/SDK misestimating decimals) sending a small enough raw `amount` — up to `10^(18-local_decimals) - 1` wei, e.g. just under 1e12 wei for a 6-decimal asset — will trigger the bug on every single such transfer. This requires no special privileges, no admin misconfiguration beyond the pallet's own required/enforced decimal relationship, and no cooperation from other parties; it is a straightforward, deterministic consequence of calling `send()` with a small amount.

### Recommendation
- Reject or round up (rather than silently floor to zero) transfers whose converted local amount would be `0`; e.g. have `convert_to_balance` return an error (`AmountTooSmall`) when the computed local balance is zero but the input `value` is non-zero, so `on_accept`/`on_timeout` can revert/refund appropriately instead of minting nothing.
- Alternatively, enforce a minimum transferable amount on the EVM `send()` side (`params.amount >= 10^(erc_decimals - local_decimals)`) validated against the configured decimals for the destination asset, before burning tokens.
- Audit `on_timeout`'s refund conversion for the same issue, since a timed-out transfer's refund is also computed via `convert_to_balance` and could similarly refund `0`.

### Proof of Concept
1. Admin registers asset `X` with `local_decimals = 6` on the substrate chain and EVM contract `erc_decimals = 18` (satisfies the `ensure!(config.decimals >= local_decimals)` check in `register_token`).
2. A user calls `HyperFungibleToken(X).send({ amount: 999_999_999_999 (i.e. < 1e12), ... })` on the EVM chain.
3. `_burn(msg.sender, 999_999_999_999)` executes — the user's tokens are gone.
4. The ISMP message with `amount = 999_999_999_999` is delivered; `on_accept` computes `erc_decimals.saturating_sub(local_decimals) = 12`, so `convert_to_balance` computes `999_999_999_999 / 10^12 = 0`.
5. `Assets::mint_into(X, beneficiary, 0)` succeeds; `TokenReceived { amount: 0, .. }` is emitted; the beneficiary receives nothing.
6. The user has permanently lost `999_999_999_999` wei worth of token `X` with no error and no way to recover it.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-282)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
    }
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L74-91)
```rust
		// Convert amount from ERC20 denomination to local
		let decimals = if local_asset_id == T::NativeAssetId::get() {
			T::Decimals::get()
		} else {
			<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
				local_asset_id.clone(),
			)
		};
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L239-255)
```rust
				let decimals = if local_asset_id == T::NativeAssetId::get() {
					T::Decimals::get()
				} else {
					<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
						local_asset_id.clone(),
					)
				};
				let erc_decimals = Precisions::<T>::get(local_asset_id.clone(), dest)
					.ok_or(HftError::DecimalsNotConfigured(dest))?;
				let amount = convert_to_balance::<
					<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance,
				>(
					U256::from_big_endian(&message.amount.to_be_bytes::<32>()),
					erc_decimals,
					decimals,
				)
				.map_err(|e| HftError::InvalidAmountConversion(format!("{e:?}")))?;
```

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L39-52)
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
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L336-355)
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
```
