### Title
Integer-division truncation in `convert_to_balance` silently drops incoming cross-chain transfers to zero - ([File: modules/pallets/hyper-fungible-token/src/impls.rs])

### Summary
`pallet-hyper-fungible-token`'s `on_accept` (and `on_timeout`) handler converts an incoming ERC20 `U256` amount to the local `Balance` type via `convert_to_balance`, which performs plain integer division by `10^(erc_decimals - local_decimals)`. Exactly like the reported `L2ECO.balanceOf` bug, any incoming amount smaller than the divisor truncates to `0`, so the pallet happily mints/transfers `0` to the beneficiary while the corresponding tokens were already permanently burned/escrowed on the EVM source chain.

### Finding Description
`convert_to_balance` divides the raw ERC20 amount by the decimal-scaling factor with no minimum-amount check and no rejection of a zero result: [1](#0-0) 

This is invoked in `on_accept` on every incoming `HyperFungibleToken`/`WrappedHyperFungibleToken` message, using the registered `Precisions` (EVM decimals) and the local asset's decimals to compute the destination amount: [2](#0-1) 

The registration/update path only requires `erc_decimals >= local_decimals`, guaranteeing the divisor is always `≥ 1` and, whenever `erc_decimals > local_decimals`, exactly the dust-truncation shape described in the report: [3](#0-2) 

On the EVM side, `HyperFungibleToken.send()` burns `params.amount` from the caller and dispatches the raw (un-scaled) amount with no minimum-amount enforcement: [4](#0-3) 

So a sender can burn a real (non-zero) amount of tokens on the EVM chain, dispatch a valid ISMP POST request, have it delivered and accepted by `pallet-hyper-fungible-token`, and yet `convert_to_balance` returns `0` because `message.amount < 10^(erc_decimals - local_decimals)`. The pallet proceeds to "mint"/"transfer" `0` to the beneficiary and still emits `TokenReceived`, treating the request as successfully and correctly settled — the burned value is permanently gone with nothing credited.

The same `convert_to_balance` call is reused in `on_timeout`, so the identical truncation risk exists on refunds as well: [5](#0-4) 

Concretely, `BridgeToken.sol` documents a scale factor of `10^6` between its 18-decimal EVM representation and BRIDGE's 12 decimals on nexus: [6](#0-5) 

Any `send()` call with `amount < 1_000_000` (in 18-decimal wei, i.e. `< 1e-12 BRIDGE`) burns real BRIDGE tokens on the EVM chain while crediting exactly `0` on nexus once delivered.

### Impact Explanation
This is a real, unbacked-burn / permanent-fund-loss condition reachable by a single unprivileged dispatched message: any account holding a `HyperFungibleToken`/`WrappedHyperFungibleToken` (or `BridgeToken`) on an EVM chain can trigger it just by calling `send()` with a sub-threshold amount. Because the message is fully valid and gets accepted (no revert, no timeout), there is no automatic refund path — the ERC20 side has irreversibly burned tokens, and the destination side mints/transfers zero. Depending on token pairs' configured decimal gaps, the "dust" threshold that gets fully swallowed can be non-trivial (e.g., up to `10^12` wei per unit for an 18-vs-6 decimal pair), so this is not purely negligible rounding — it is a full loss of the transferred value for any transfer at or below the threshold, satisfying "unbacked mint"/"permanent freezing (loss) of funds" criteria.

### Likelihood Explanation
Likelihood is Medium: the truncation is deterministic and trivially triggerable by any user constructing a `send()` call with a small enough amount (no special privileges, no race conditions, no reliance on relayer or governance behavior). It is not an attack against a victim's funds (the caller loses their own tokens), which slightly tempers severity versus a griefing/attack vector, but it still represents a genuine, protocol-level fund-loss bug identical in root cause to the referenced L2ECO issue, and it is present on every EVM↔pallet token pair configured with `erc_decimals > local_decimals` (i.e., essentially every real deployment, since 18-decimal EVM tokens are paired against lower-decimal or equal-decimal substrate assets).

### Recommendation
In `convert_to_balance` (and its call sites in `on_accept`/`on_timeout`), reject conversions that truncate to zero for a non-zero input, e.g. return an error (causing the ISMP handler to fail, which allows retry/relayer-side correction) rather than silently proceeding with amount `0`. Additionally, consider enforcing a minimum transferable amount at the EVM `send()` layer (reject `amount < 10^(erc_decimals - local_decimals)`) so the burn never occurs for amounts that cannot be represented on the destination chain.

### Proof of Concept
1. Register a token pair where `erc_decimals = 18` and the local asset's `decimals = 6` (a common real-world configuration, e.g. as in `BridgeToken.sol`'s 18-vs-12-decimal scaling comment).
2. On the EVM chain, call `HyperFungibleToken.send({ amount: 999_999, ... })` (i.e., `amount < 10^12`). This burns `999_999` wei of the token and dispatches an ISMP POST request carrying `message.amount = 999_999`.
3. The relayer delivers the request; `pallet-hyper-fungible-token::on_accept` runs, computing `erc_decimals.saturating_sub(local_decimals) = 12`, so `convert_to_balance` computes `999_999 / 10^12 = 0`.
4. The pallet transfers/mints `0` to the beneficiary and emits `TokenReceived { amount: 0, .. }`. The sender's `999_999` wei is permanently lost — burned on the EVM chain, never credited on the destination. [7](#0-6) [8](#0-7)

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L218-255)
```rust
	fn on_timeout(&self, request: Request) -> Result<Weight, anyhow::Error> {
		match request {
			Request::Post(PostRequest { body, to, dest, .. }) => {
				let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;

				// Refund the original sender
				let from_bytes = message.from.as_ref();
				let mut sender_bytes = [0u8; 32];
				if from_bytes.len() == 32 {
					sender_bytes.copy_from_slice(from_bytes);
				} else if from_bytes.len() == 20 {
					sender_bytes[12..].copy_from_slice(from_bytes);
				} else {
					Err(HftError::InvalidSenderLength(from_bytes.len()))?
				}
				let beneficiary: T::AccountId = sender_bytes.into();

				// Look up the asset from the destination contract address
				let local_asset_id = ContractToAsset::<T>::get(dest, &to)
					.ok_or(HftError::UnknownContractOnTimeout)?;

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L350-355)
```rust
					return Err(Error::<T>::NonEvmPeerChain.into());
				}
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L293-311)
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

**File:** evm/src/apps/BridgeToken.sol (L34-36)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```
