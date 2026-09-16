### Title
Precision truncation on cross-chain token receipt permanently burns dust when EVM-side decimals exceed local pallet decimals - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`HyperFungibleToken.send()` on the EVM side burns an arbitrary, user-supplied `uint256` amount with no rounding to the destination chain's decimal grid. When that message is delivered to `pallet-hyper-fungible-token`'s `on_accept`, the amount is scaled down from EVM (`erc_decimals`) precision to local (`decimals`) precision via integer division in `convert_to_balance`, which silently truncates any remainder. The truncated fraction was already irrevocably burned/locked on the EVM side but is never credited to the beneficiary or refunded to anyone on the destination chain — it is permanently lost, exactly the "small amounts burned when bridging" bug class described in the external report.

### Finding Description
On the EVM side, `HyperFungibleToken.send()` burns `params.amount` unconditionally: [1](#0-0) 

`params.amount` is an arbitrary caller-supplied `uint256` with no constraint that it be a multiple of the scaling factor between the EVM token's decimals and the destination chain's decimals.

On the Substrate side, `on_accept` looks up `erc_decimals` (the EVM-side precision recorded in `Precisions`) and the local asset's `decimals`, then converts the incoming amount with `convert_to_balance`: [2](#0-1) 

`convert_to_balance` performs a floor division and drops the remainder entirely: [3](#0-2) 

Because the division factor is `10 ** (erc_decimals - local_decimals)`, any incoming `amount` that is not an exact multiple of that factor has its low-order digits discarded with no accounting: the beneficiary is minted/credited `amount / factor` (rounded down), while the sender already burned/escrowed the full, un-rounded `amount` on the EVM side. There is no dust bucket, refund, or event capturing the discarded remainder — it is silently destroyed. This is precisely the documented cross-decimals caveat the pallet's own README calls out ("Decimals between this chain and each remote chain may differ; per-pair `Precisions` storage records the EVM-side decimals so amounts get scaled at the boundary") without any corresponding rounding safeguard on the sending side.

`BridgeToken.sol`, the concrete BRIDGE token deployment, confirms this is a live production configuration: EVM side is 18 decimals while nexus (Substrate) is 12 decimals, a 6-decimal gap: [4](#0-3) 

Any `send()` call with an amount whose last 6 decimal digits are non-zero (e.g. `1000000000001` wei of BRIDGE) burns the full amount on EVM, and `on_accept` on nexus mints/releases only the floor-divided amount, permanently destroying the truncated remainder. The same mechanism applies to `on_timeout` refunds (also driven by `convert_to_balance`), though that path is self-consistent for the "send-then-timeout" round trip since the same conversion factor reverses cleanly there; the loss occurs on the forward `on_accept` mint/release path whenever the inbound message amount is not already a multiple of the scale factor.

### Impact Explanation
Every cross-chain transfer where the EVM-side token decimals exceed the destination pallet's local asset decimals, and the transferred amount is not an exact multiple of the resulting scale factor, permanently destroys the truncated fraction. This is systemic (affects any registered asset pair with a nonzero, positive decimal gap, including the production `BridgeToken`/nexus configuration) and requires no privileged access — any ordinary token bridger triggers it simply by sending a non-round amount. Funds are permanently lost with no recovery path, matching Medium impact as in the referenced report.

### Likelihood Explanation
Likelihood is Medium-to-High in practice: wallets and users routinely send amounts that are not round multiples of large scale factors (e.g., swap outputs, fee-adjusted amounts, or amounts computed by other on-chain logic), and nothing in `HyperFungibleToken.send()`, `WrappedHyperFungibleToken`, or the pallet's `send` extrinsic pre-validates or rounds the amount to the destination's precision grid before burning/locking.

### Recommendation
Before burning/locking on the sending side (or immediately after receiving on the destination side), round the amount down to the nearest multiple of the decimal scale factor and either revert on a non-zero remainder or refund/return the dust to the sender, mirroring the recommended pattern from the report:
```solidity
uint256 factor = 10 ** extraDecimals;
uint256 roundedAmount = amount - (amount % factor);
require(roundedAmount > 0, "DustAmount");
_burn(msg.sender, roundedAmount);
```
On the Substrate side, `convert_to_balance` should either reject amounts with a non-zero remainder or the caller (`on_accept`/`on_timeout`) should account for and refund the truncated dust instead of discarding it silently.

### Proof of Concept
1. Register an asset pair where `erc_decimals` (EVM) = 18 and local pallet `decimals` = 12 (as documented for `BridgeToken`/nexus in [4](#0-3) ).
2. A user calls `HyperFungibleToken.send()` (or `BridgeToken` inherited `send`) with `amount = 1_000_000_000_001` wei (not a multiple of `10^6`).
3. `send()` burns the full `1_000_000_000_001` from the caller: [5](#0-4) 
4. The ISMP message carries `amount = 1_000_000_000_001` to nexus.
5. `on_accept` computes `convert_to_balance(1_000_000_000_001, 18, 12)` = `1_000_000_000_001 / 10^6` = `1_000_000` (floor), discarding `000_000_000_001` remainder permanently: [6](#0-5) 
6. The beneficiary receives tokens equivalent to `1_000_000_000_000` wei worth, while `1_000_000_000_001` wei was burned on EVM — the `1` wei difference (scaled) is permanently lost with no event, refund, or recovery mechanism.

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

**File:** evm/src/apps/BridgeToken.sol (L33-36)
```text
 *
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```
