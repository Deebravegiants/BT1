### Title
Truncating decimal conversion on `pallet-hyper-fungible-token` incoming transfers permanently burns dust when EVM amount is not an exact multiple of the scaling factor - ([File: modules/pallets/hyper-fungible-token/src/impls.rs])

### Summary
`convert_to_balance` in `pallet-hyper-fungible-token` truncates (integer-divides) when scaling an incoming ERC20 `U256` amount down to the pallet's local balance precision. Because the source-chain `HyperFungibleToken`/`WrappedHyperFungibleToken` contracts burn/lock the *exact* amount specified by the sender with no requirement that it be a multiple of `10^(erc_decimals - local_decimals)`, an attacker or an ordinary user can dispatch a message whose amount, once divided back down on `on_accept`, loses the remainder. That remainder is neither minted/released to the beneficiary nor accounted for anywhere — it is permanently lost, mirroring the reported HGT rounding-down bug where the debited amount does not match the credited amount.

### Finding Description
`convert_to_balance` performs plain integer division with no remainder handling: [1](#0-0) 

It is invoked directly on the untrusted `message.amount` decoded from an incoming ISMP `PostRequest` in both `on_accept` and `on_timeout`: [2](#0-1) [3](#0-2) 

The counterpart escrow/burn on the EVM side (`HyperFungibleToken`/`WrappedHyperFungibleToken`) transfers/burns exactly `amount` as specified by the caller with no constraint that it be divisible by the decimals-scaling factor — the `SendParams.amount` field is a free-form `uint256`: [4](#0-3) 

Because `register_token`/`update_token` only enforce `erc_decimals >= local_decimals` (not equality), a scaling factor `10^(erc_decimals - local_decimals) > 1` is a normal, expected configuration (as documented for `BridgeToken`, which is 18 decimals on EVM vs 12 on nexus, i.e. scale `10^6`): [5](#0-4) [6](#0-5) 

Any sender who dispatches an ISMP POST whose `Message.amount` is not an exact multiple of that scaling factor (e.g. `100 * 10^18 + 1` instead of a clean `100 * 10^18` for BRIDGE) causes `convert_to_balance` to silently floor the amount, so `mint_into`/`transfer` on the beneficiary credits strictly less than what was escrowed/burned on the source chain. The dust wei(s) are dropped with no event, no residual balance tracked, and no path to recover them — a permanent, unbacked loss of value on every such delivery. This is fully reachable by an unprivileged relayer delivering a message that originated from an unprivileged sender's `send()` call (the source-chain contract does not validate amount divisibility), so it requires no special privilege beyond normal message dispatch and relay.

### Impact Explanation
Each cross-chain transfer whose amount is not a clean multiple of the decimals scale factor permanently destroys the fractional remainder: it is burned/escrowed on the source chain but never minted/released on the destination. Over many transfers (an ordinary, expected occurrence given users specify arbitrary 18-decimal amounts against pallets with lower-precision assets, e.g. 6 or 12 decimals) this compounds into a growing, permanently frozen shortfall between the source-chain circulating supply/escrow and what beneficiaries actually received — the same class of impact ("off-by-N wei debits more/mints less than specified, imbalance builds up over time") flagged in the reference report. This satisfies the "permanent freezing of funds" / "unbacked mint or burn imbalance" criteria.

### Likelihood Explanation
High likelihood: no privileged role is required. Any user calling the standard `send()`/`bridge()` flow on the EVM `HyperFungibleToken` with a non-round amount (which the SDK does not enforce to be divisible by the scale factor) triggers this on delivery. Given `parseEther`-based user-supplied amounts are common and the documented `BridgeToken` scale factor is `10^6`, hitting a non-multiple amount is the default case rather than an edge case.

### Recommendation
Either (a) reject/round messages whose ERC20 amount is not an exact multiple of `10^(erc_decimals - local_decimals)` in `on_accept`/`on_timeout` (returning an error so the request is refused rather than silently truncated), or (b) explicitly track and refund/credit the truncated remainder (e.g. accumulate dust in a per-asset escrow account redeemable later), and enforce the same divisibility check on the EVM side's `send()` so a sender cannot submit an amount that would truncate on delivery in the first place.

### Proof of Concept
1. Register a non-native asset with `local_decimals = 12` and `erc_decimals = 18` for an EVM chain (scale factor `10^6`), as done for `BridgeToken`/nexus.
2. A user calls `HyperFungibleToken.send()` on the EVM side with `amount = 100 * 10^18 + 1` (not a multiple of `10^6`) — the contract burns exactly this amount with no divisibility check, and the ISMP `Message.amount` encodes `100000000000000000001`.
3. The relayer delivers the request; `pallet-hyper-fungible-token::on_accept` calls `convert_to_balance(U256::from(100000000000000000001), 18, 12)`, which computes `100000000000000000001 / 10^6 = 100000000000000` (floor), dropping the trailing `000001` remainder.
4. The beneficiary is minted/credited `100000000000000` (in 12-decimal units) — exactly equivalent to `100 * 10^18` in ERC20 units — while `100 * 10^18 + 1` was burned on the source chain. The 1 wei (and, in general, up to `scale_factor - 1` wei per transfer) is permanently lost with no event or accounting trail.

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L51-67)
```text
    struct SendParams {
        /// @notice Destination chain identifier (e.g., StateMachine.evm(1))
        bytes dest;
        /// @notice Recipient account on the destination chain
        bytes to;
        /// @notice Amount of tokens to send
        uint256 amount;
        /// @notice Timeout duration in seconds for the cross-chain message
        uint64 timeout;
        /// @notice Fee paid to relayers for message delivery
        uint256 relayerFee;
        /**
         * @notice Optional calldata to execute on the destination chain via CallDispatcher.
         * Should be an abi-encoded Call[] array.
         */
        bytes data;
    }
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L352-355)
```rust
				ensure!(
					config.decimals >= local_decimals,
					Error::<T>::ErcDecimalsBelowLocal
				);
```

**File:** evm/src/apps/BridgeToken.sol (L34-36)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```
