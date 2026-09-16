Confirmed: no zero-amount check anywhere in `on_accept` or `on_timeout` before performing the transfer/mint. This confirms the analog is valid and reachable via a single EVM transaction from an unprivileged user.

### Title
Cross-chain amount truncates to zero in `pallet-hyper-fungible-token::on_accept` while the source chain already burned the full amount - permanent loss of dust-range transfers (File: `modules/pallets/hyper-fungible-token/src/module.rs`, `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`pallet-hyper-fungible-token`'s `on_accept` handler converts an incoming ERC20-denominated amount to the local balance denomination via `convert_to_balance`, which performs a plain integer division to scale down precision. If the message amount is smaller than the scaling factor, the result truncates to zero, yet the pallet still proceeds to "mint"/"transfer" that zero amount and emits `TokenReceived` as if delivery succeeded — with no check that the converted amount is non-zero. Because the corresponding `HyperFungibleToken.send()` call on the EVM source chain has already unconditionally burned the caller's full `params.amount` before dispatch, any inbound amount that rounds to zero after conversion results in a permanent, unrecoverable loss of the sender's tokens.

### Finding Description
The vulnerable conversion helper: [1](#0-0) 

divides the incoming `U256` ERC20 amount by `10^(erc_decimals - local_decimals)` with no floor/zero check. In `on_accept`, this converted `amount` is used directly for the mint/transfer with no validation that it is non-zero: [2](#0-1) 

and the `TokenReceived` event is emitted unconditionally, reporting success even when `amount == 0`: [3](#0-2) 

The paired EVM-side `send()` function unconditionally burns the caller's entire specified `params.amount` from their balance before dispatching the ISMP request — there is no minimum-amount or post-conversion check on the EVM side either, since the scaling only happens on the receiving pallet: [4](#0-3) 

Concretely: for a token registered with `erc_decimals = 18` (the documented EVM convention) and a substrate `local_decimals` of `10` or `12` (e.g. DOT/KSM-style native currencies), the scaling factor in `convert_to_balance` is `10^8` or `10^6`. Any `message.amount` strictly less than that factor (i.e., real, non-zero wei values, e.g. `1` to `99_999_999` wei for the `10^8` case) truncates to a local balance of exactly `0`. The EVM side has already burned that exact `params.amount` of tokens from the sender in `send()`, but the destination substrate chain mints/unlocks `0` to the beneficiary — the tokens are burned with nothing delivered, and there is no error, revert, or refund path triggered (the request is recorded as successfully "accepted", not timed out), so the standard timeout-refund mechanism in `on_timeout` never fires either.

The same rounding-to-zero pattern also exists on the `on_timeout` refund path (`convert_to_balance` reused identically), meaning even the *refund* for an undelivered/timed-out request can round to zero and never actually return escrowed funds to the original sender: [5](#0-4) 

This is directly analogous to the referenced `USSD.mintForToken()` issue: a value is unconditionally debited/burned from the user based on the raw input amount, then a second calculation (decimal-precision conversion) can independently round the credited amount down to zero, and the code does not guard against that outcome before finalizing the transfer.

### Impact Explanation
Any unprivileged user who calls `HyperFungibleToken.send()` (or the substrate `send()` extrinsic in the reverse direction) with an amount that falls below the source→destination decimal scaling factor loses those tokens permanently: they are burned/escrowed on the source chain, but the destination pallet credits `0` to the beneficiary while still recording the request as successfully delivered. Because delivery is recorded as accepted (not failed/timed-out), there is no automatic path to recover the burned funds via the `on_timeout` refund mechanism. This is a direct, unbacked loss of user funds reachable from a single cross-chain token transfer — meeting the "concrete theft or permanent freezing of funds" bar.

### Likelihood Explanation
This requires no privileged role, no consensus/relayer collusion, and no special conditions beyond sending an amount within a specific dust range relative to the configured chain decimals (a range of ~10^6–10^8 possible wei values per affected token pair, easily hit by user error, a misconfigured client that doesn't account for decimal scaling, dust-sweeping bots, or an attacker deliberately griefing another user's `to` address to have their outgoing message register as "delivered" with a zero credit). The relevant conversion functions are called on every single `on_accept`/`on_timeout` invocation for non-native-decimal-matched chains, so the bug is present on essentially every real deployment where EVM (18 decimals) bridges to a substrate chain with fewer native decimals (10 or 12, the documented common case).

### Recommendation
Add an explicit non-zero check on the converted `amount` in both `on_accept` and `on_timeout` in `modules/pallets/hyper-fungible-token/src/module.rs` immediately after calling `convert_to_balance`, and reject the request (return an error, e.g. a new `HftError::AmountTooSmall`) rather than silently proceeding with a zero-value mint/transfer. Since a rejected `on_accept` causes the request to be treated as undeliverable and eligible for the sender's timeout-refund path, this at minimum converts a silent, permanent loss into a recoverable timeout. Consider additionally enforcing a minimum transferable amount check on the EVM `send()` / substrate `send()` paths themselves (before burning), by having the sender-side code perform the same decimal conversion the destination will apply and reverting if it would round to zero, so the loss can never be initiated in the first place.

### Proof of Concept
1. Register an HFT asset pair where the EVM contract's `erc_decimals` for the destination-recorded `Precisions` value is `18` (standard EVM convention) and the substrate chain's native `Decimals::get()` is `10` (e.g., a DOT-style native currency), per the documented runtime config in `modules/pallets/hyper-fungible-token/README.md`.
2. On the EVM chain, a user (e.g., attacker or a user who fat-fingers a decimal) calls `HyperFungibleToken.send(SendParams{ dest: <substrate-chain>, to: <beneficiary bytes>, amount: 1, timeout: ..., relayerFee: 0, data: "" })` — `amount = 1` wei is burned unconditionally from the caller in `send()` (see `HyperFungibleToken.sol:264-282`).
3. The relayer delivers the resulting `PostRequest` (with `message.amount = 1`) to the substrate `pallet-hyper-fungible-token` via `on_accept`.
4. Inside `on_accept`, `convert_to_balance(U256::from(1), erc_decimals=18, local_decimals=10)` computes `1 / 10^8 = 0` (integer division). `amount = 0`.
5. `NativeCurrency::transfer(pallet_account, beneficiary, 0, ...)` succeeds trivially; `TokenReceived { beneficiary, amount: 0, source }` is emitted; the request commitment is recorded as accepted/delivered.
6. Net result: the EVM sender's balance decreased by `1` wei permanently; the substrate beneficiary received `0`; no timeout/refund is ever triggered because the request was accepted, not rejected — the funds are unrecoverably lost.

### Citations

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L74-117)
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L205-211)
```rust
		Self::deposit_event(Event::<T>::TokenReceived {
			beneficiary,
			amount: amount.into(),
			source,
		});

		Ok(T::DbWeight::get().reads_writes(5, 2))
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L238-285)
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

				// Refund: release escrowed tokens back to the original sender
				if local_asset_id == T::NativeAssetId::get() {
					<T as Config>::NativeCurrency::transfer(
						&Pallet::<T>::pallet_account(),
						&beneficiary,
						amount.into(),
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
						<T as Config>::Assets::mint_into(
							local_asset_id,
							&beneficiary,
							amount.into(),
						)
						.map_err(|e| HftError::MintFailed(e.into()))?;
					}
				}
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L258-282)
```text
    /**
     * @dev Burns `params.amount` from the caller and sends an ISMP POST request to the
     * destination chain. Fees can be paid in native tokens (via msg.value) or in the
     * host's fee token (pulled from msg.sender).
     * @param params The send parameters including destination, recipient, amount, and optional calldata
     */
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
