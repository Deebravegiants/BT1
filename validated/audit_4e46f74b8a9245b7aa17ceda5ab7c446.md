### Title
Decimal-truncation in `pallet-hyper-fungible-token`'s ERC20→local conversion silently burns user funds when bridging sub-scale amounts - ([File: modules/pallets/hyper-fungible-token/src/impls.rs])

### Summary
`HyperFungibleToken`/`BridgeToken.send()` on EVM chains burns an arbitrary `uint256` amount and dispatches it unchanged to the paired Substrate pallet. The receiving pallet's `on_accept` converts that ERC20-denominated amount to the local balance type by floor-dividing by `10^(erc_decimals - local_decimals)`. Neither side enforces a minimum transferable amount, so a user who bridges an amount smaller than the scaling factor has their tokens burned on the source chain while the destination mints/credits zero — an unrecoverable loss, directly analogous to the reported `SolverVault::requestWithdraw()` rounding-to-zero bug.

### Finding Description
`BridgeToken` documents that BRIDGE is 12 decimals on nexus (Substrate) while the EVM-side ERC20 representation uses the default 18 decimals, so "the pallet scales by 10^6 in both directions": [1](#0-0) 

The EVM `send()` function (inherited from `HyperFungibleToken`/`HyperFungibleTokenUpgradeable`) burns `params.amount` from the caller with no minimum-amount validation, then dispatches an ISMP POST carrying that raw 18-decimal amount: [2](#0-1) 

On the Substrate side, `pallet_hyper_fungible_token`'s `on_accept` computes the local credit amount via `convert_to_balance`, which performs an integer division to scale down from the 18-decimal ERC20 amount to the 12-decimal local balance: [3](#0-2) 

`convert_to_balance` itself does a plain floor division with no zero-amount check or revert: [4](#0-3) 

`register_token`/`update_token` only enforce `config.decimals >= local_decimals` (i.e. `erc_decimals >= local_decimals` is guaranteed), which is exactly the precondition under which this floor-division truncation to zero can occur for small amounts: [5](#0-4) 

`on_accept` proceeds to mint/transfer `amount` (which may be `0`) to the beneficiary and emits `TokenReceived` unconditionally — there is no revert or rejection path when the converted amount rounds to zero: [6](#0-5) 

Because `10^(erc_decimals - local_decimals) = 10^6` for BRIDGE, any ERC20 amount in the range `1` to `999_999` wei (i.e., less than one local unit) truncates to `0` upon arrival, while the equivalent tokens were already irrevocably burned on the EVM side in `send()`.

### Impact Explanation
This is a direct, unprivileged loss of user funds: any external account can call `send()` on `BridgeToken` (or any `HyperFungibleToken` deployment configured with `erc_decimals > local_decimals`) with an amount below the scaling factor, burning real value on the source chain and receiving nothing on the destination chain. This is not an admin/governance/relayer-privileged bug — it is directly reachable by any token bridger performing a single cross-chain transfer, matching the "unbacked burn / permanent freezing of funds" impact bar required for this scan.

### Likelihood Explanation
Likelihood is high for accidental loss (fat-fingered amounts, off-by-decimal UI bugs, or programmatic integrations that don't account for the 10^6 scale factor) and is trivially triggerable by an attacker who simply wants to grief a specific account by front-running/observing that no minimum-amount guard exists. No special privileges, timing, or coordination are required — a single `send()` call with `amount < 10^(erc_decimals - local_decimals)` is sufficient.

### Recommendation
- In `HyperFungibleToken.send()` / `HyperFungibleTokenUpgradeable.send()`, reject amounts that are not exact multiples of the destination's known scaling factor (or reject amounts below it), or perform the same conversion locally before burning and revert if the result is zero.
- In `pallet_hyper_fungible_token::module::on_accept` (and the equivalent path in `on_timeout`), explicitly check that `convert_to_balance` does not return zero when the input `U256` amount is non-zero, and reject (`Err`) the message rather than crediting/refunding zero, so the relayer/sender is aware the transfer failed rather than silently losing funds.
- Consider requiring `erc_decimals == local_decimals`, or publishing the required minimum transfer unit via a query so integrators/UIs can pre-validate amounts before burning.

### Proof of Concept
1. Deploy `BridgeToken` on an EVM chain where `decimals() == 18`; register it as a peer of nexus's `pallet-hyper-fungible-token`, which holds BRIDGE with `T::Decimals = 12`, so `Precisions` for this chain is configured to `18` (consistent with the contract comment at `evm/src/apps/BridgeToken.sol:34-36`).
2. A user calls `send({ amount: 500000, dest: nexus, to: beneficiary, ... })` (i.e., `500_000 < 10^6`).
3. `_burn(msg.sender, 500000)` executes successfully in `HyperFungibleTokenUpgradeable.send()` (`sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol:293-294`), and the ISMP POST is dispatched carrying `amount = 500000` (18-decimal denomination).
4. On nexus, `on_accept` computes `erc_decimals = 18`, `decimals = 12`, and calls `convert_to_balance(500000, 18, 12)`, which divides `500000` by `10^6 = 1_000_000`, yielding `0` (`modules/pallets/hyper-fungible-token/src/impls.rs:43-52`, `modules/pallets/hyper-fungible-token/src/module.rs:82-91`).
5. `on_accept` proceeds to transfer/mint `0` to the beneficiary and emits `TokenReceived { amount: 0, ... }` without reverting (`modules/pallets/hyper-fungible-token/src/module.rs:93-117`).
6. Net effect: the user's 500000-wei BRIDGE was burned on the EVM chain, and the beneficiary received 0 BRIDGE on nexus — a permanent loss of the user's funds.

### Citations

**File:** evm/src/apps/BridgeToken.sol (L34-36)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L293-302)
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L93-117)
```rust
		// Mint or transfer to beneficiary
		if local_asset_id == T::NativeAssetId::get() {
			<T as Config>::NativeCurrency::transfer(
				&Pallet::<T>::pallet_account(),
				&beneficiary,
				amount,
				ExistenceRequirement::AllowDeath,
			)
			.map_err(|e| HftError::TransferFailed(e.into()))?;
		} else {
			let is_native = NativeAssets::<T>::get(local_asset_id.clone());
			if is_native {
				<T as Config>::Assets::transfer(
					local_asset_id,
					&Pallet::<T>::pallet_account(),
					&beneficiary,
					amount.into(),
					Preservation::Expendable,
				)
				.map_err(|e| HftError::TransferFailed(e.into()))?;
			} else {
				<T as Config>::Assets::mint_into(local_asset_id, &beneficiary, amount.into())
					.map_err(|e| HftError::MintFailed(e.into()))?;
			}
		}
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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L352-355)
```rust
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
```
