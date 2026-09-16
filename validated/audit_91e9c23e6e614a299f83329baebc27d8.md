### Title
Silent truncation of cross-chain amounts to zero in `pallet-hyper-fungible-token` causes permanent loss of bridged funds - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`, `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`pallet-hyper-fungible-token`'s `on_accept` and `on_timeout` handlers convert an incoming ERC20 `U256` amount to the local balance type via `convert_to_balance`, which performs an unchecked integer division. When the ERC20 side has more decimal precision than the local asset, any amount smaller than the scaling factor truncates to exactly `0`, yet the pallet proceeds to `mint_into`/`transfer`/refund `0` and still emits a success event, with no check that the converted amount is non-zero. This mirrors the reported Lido `WstETH` bug class where a share/amount conversion can silently yield zero and is used without a `> 0` guard.

### Finding Description
`convert_to_balance` divides the ERC20 `U256` value by `10^(erc_decimals - local_decimals)` with no zero check on the result: [1](#0-0) 

`on_accept` calls this conversion and, without validating `amount > 0`, unconditionally mints or transfers the (possibly zero) result to the beneficiary and emits `TokenReceived`: [2](#0-1) [3](#0-2) 

The same unguarded conversion is used in `on_timeout` for refunds: [4](#0-3) 

The `send` extrinsic already escrowed or burned the *full* local amount on the source chain before dispatching the ISMP request; the corresponding EVM `HyperFungibleToken.send()`/`BridgeToken` counterpart likewise burns the full `params.amount` before dispatch: [5](#0-4) 

Because chains can be configured with different decimal precisions (documented example: BRIDGE is 18 decimals on EVM but 12 decimals on nexus, a 10^6 scaling factor): [6](#0-5) 

any amount dispatched from the higher-precision chain that is smaller than the scale factor (e.g. `< 1_000_000` wei of an 18-decimal token bridging to a 12-decimal asset) truncates to `0` on arrival. The source side has already irreversibly burned/escrowed the non-zero amount, but the destination side credits nothing, and the ISMP request is still considered successfully delivered (no revert, no error path) — so the sender cannot reclaim funds via timeout either, since the request was accepted, not timed out.

### Impact Explanation
This causes a genuine, irrecoverable loss of user funds reachable from a single unprivileged cross-chain transfer: any account (or contract) that dispatches a dust-sized `send()`/`send` extrinsic across a decimal-mismatched token pair burns or escrows real value on the source chain while the destination chain silently mints/transfers zero, with a `TokenReceived`/`Sent` event still fired as if the transfer succeeded. This is a permanent freezing/loss-of-funds bug that requires no special privilege and is directly analogous to the reported "amount potentially zero" class from the external report, which also results in silently accepting worthless zero-value operations.

### Likelihood Explanation
Likelihood is high for any token pair registered with differing EVM/substrate decimal precision (a documented, expected configuration per the pallet's `Precisions` storage and the `BridgeToken` 18↔12 decimal example). Any unprivileged user or automated relayer/bot can trigger the truncation simply by sending an amount below the scale factor — no governance or admin cooperation is required, and the bug is triggered purely by normal usage of the documented cross-chain `send` flow.

### Recommendation
Add an explicit non-zero check after `convert_to_balance` in both `on_accept` and `on_timeout` (and mirror it in the `send` extrinsic's `convert_to_erc20` path for symmetry), reverting the message processing (or refusing to deliver) when the destination-side converted amount is zero, e.g.:
```rust
let amount = convert_to_balance::<...>(...)
    .map_err(|e| HftError::InvalidAmountConversion(format!("{e:?}")))?;
ensure!(!amount.is_zero(), HftError::ZeroAmountAfterConversion);
```
Additionally consider enforcing a minimum transferable amount at the `send` extrinsic (source side) computed from the destination's configured decimals, so dust that would round to zero is rejected before funds are ever escrowed/burned.

### Proof of Concept
1. Register a token with `native = false` (or the native asset) where the EVM peer uses 18 decimals and the substrate side uses 12 decimals (10^6 scale), as documented for `BridgeToken`.
2. From the EVM side, call `send()`/`BridgeToken.send()` with `amount = 999_999` wei (less than the 10^6 scale factor). The contract burns `999_999` wei and dispatches a POST request carrying that raw amount.
3. On delivery, `pallet-hyper-fungible-token::on_accept` computes `convert_to_balance(999_999, 18, 12)` → `999_999 / 10^6 = 0`.
4. The pallet calls `mint_into`/`transfer` with `amount = 0`, which succeeds, and emits `TokenReceived { amount: 0, .. }`.
5. Result: `999_999` wei of the source token is permanently burned/escrowed with zero credited to the beneficiary, and the request is not eligible for a timeout refund since delivery succeeded.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L43-52)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L82-117)
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L246-292)
```rust
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

				Pallet::<T>::deposit_event(Event::<T>::TokenRefunded {
					beneficiary,
					amount: amount.into(),
					dest,
				});
				Ok(T::DbWeight::get().reads_writes(5, 2))
```

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

**File:** evm/tests/foundry/BridgeTokenTest.t.sol (L61-68)
```text

    function testMetadataIsFixedInTheBytecode() public view {
        assertEq(bridge.name(), "Hyperbridge");
        assertEq(bridge.symbol(), "BRIDGE");
        // 18 here while BRIDGE is 12 decimals on nexus, so the pallet scales by 10^6 in
        // both directions and `register_token` must declare 18 for this contract.
        assertEq(bridge.decimals(), 18);
    }
```
