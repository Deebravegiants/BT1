This is a real finding. `convert_to_balance` in `modules/pallets/hyper-fungible-token/src/impls.rs` divides an ERC20 `U256` amount by `10^(erc_decimals - local_decimals)` to scale it down to the pallet's local balance type when a token bridge mint message arrives from an EVM chain [1](#0-0) . Unlike `BandwidthManager.purchase()`, which explicitly reverts with `PriceNotRepresentable()` when a division would truncate `total18d % scale != 0` [2](#0-1) , and unlike `IntentGatewayV2`'s protocol-fee/surplus-share divisions where the floor-rounded remainder is deterministically credited to the *other* party rather than lost (so no value disappears) [3](#0-2) , `convert_to_balance` has no minimum-amount guard and no remainder handling — any locked/burned amount smaller than `10^(erc_decimals - local_decimals)` truncates silently to `0`.

### Title
Loss of precision in `convert_to_balance` allows locking ERC20 tokens on the source chain while minting zero on Hyperbridge - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
`convert_to_balance` performs `value / U256::from(10u128.pow(erc_decimals - local_decimals))` with plain integer division and no check that the division is exact or that the result is non-zero [4](#0-3) .

### Finding Description
When a bridged transfer/deposit message from an EVM-side hyper-fungible-token contract is decoded on Hyperbridge, the pallet uses `convert_to_balance` to scale the incoming `U256` ERC20 amount down to the local balance's decimal precision. If `erc_decimals > local_decimals`, the divisor is `10^(erc_decimals - local_decimals)`. Any incoming amount smaller than that divisor computes to `0` in local balance terms, and any amount that is not an exact multiple of the divisor silently drops the remainder — there is no minimum-amount enforcement and no revert-on-non-representable-value check, unlike the analogous scaling logic in `BandwidthManager.sol` which explicitly reverts with `PriceNotRepresentable()` on the same class of truncation [5](#0-4) . Because the message dispatch/lock on the EVM side is driven by the full, unscaled ERC20 amount, an attacker (or even innocent user sending dust) can lock/burn a nonzero amount of the source-chain token while causing this pallet to mint (or credit) zero (or a truncated amount less than what was locked) on Hyperbridge, permanently freezing the truncated difference with no path to reclaim it.

### Impact Explanation
This is reachable directly from a token bridge mint/burn message dispatched by any unprivileged actor sending an inbound token-bridge transfer through `EvmHost`/`HandlerV2` delivery. Repeated small transfers or a single transfer whose amount is not a clean multiple of the decimal-scaling factor cause a permanent loss (freezing) of the truncated difference — user funds are locked on the source chain without being credited on the destination, which is a concrete freezing-of-funds bug matching the "Medium" impact bar (funds not stolen by an attacker, but permanently lost/frozen for the depositor).

### Likelihood Explanation
Likelihood is high for typical deployments where the bridged ERC20 uses more decimals than the local Hyperbridge asset (e.g., 18-decimal token bridged into a 6- or 10-decimal local balance, similar to the exact scenario the `BandwidthManager` test suite calls out as `PriceNotRepresentable`) [6](#0-5) . Any transfer amount not aligned to the scaling factor, or below it, triggers the truncation with no revert, no event, and no way for the pallet to know value was lost.

### Recommendation
Mirror the `BandwidthManager.sol` pattern: before dividing, verify `value % divisor == 0` (or at minimum `value >= divisor`) and reject/return an error rather than silently minting less than deposited. Alternatively, require the EVM-side lock amount to already be pre-scaled/validated to be an exact multiple of the decimal difference, and reject transfers below the minimum representable unit at the point of dispatch on the source chain, consistent with how `BandwidthManager.purchase()` reverts with `PriceNotRepresentable()`.

### Proof of Concept
1. Deploy the hyper-fungible-token bridge between an EVM chain (18-decimal ERC20) and a Hyperbridge-side asset configured with fewer decimals, e.g. `local_decimals = 6` → divisor `= 10^12`.
2. An attacker (or any user) dispatches a bridge transfer/lock of `999_999_999_999` (i.e., `10^12 - 1`) units of the ERC20 token — a nonzero amount fully locked/burned on the EVM side.
3. On delivery, the pallet calls `convert_to_balance(U256::from(999_999_999_999), 18, 6)`, computing `999_999_999_999 / 10^12 = 0`.
4. Zero balance is credited to the recipient on Hyperbridge while the full ERC20 amount remains locked/burned on the source chain — funds are permanently frozen with no revert or refund path. [7](#0-6)

### Citations

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

**File:** evm/src/apps/BandwidthManager.sol (L163-168)
```text
        uint256 total18d = price18d * months;
        address feeToken = IDispatcher(_host).feeToken();
        uint8 dec = IERC20Metadata(feeToken).decimals();
        uint256 scale = 10 ** (18 - dec);
        if (total18d % scale != 0) revert PriceNotRepresentable();
        uint256 amount = total18d / scale;
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L424-434)
```text
    /// @dev Splits overpayment between protocol and beneficiary. An order with output calldata
    /// gives the beneficiary nothing, since the surplus is not the caller's to give.
    function _splitSurplus(uint256 dust, bool hasOutputCall)
        internal
        view
        returns (uint256 protocolShare, uint256 beneficiaryShare)
    {
        if (hasOutputCall) return (dust, 0);
        protocolShare = (dust * _params.surplusShareBps) / 10_000;
        beneficiaryShare = dust - protocolShare;
    }
```

**File:** evm/tests/foundry/BandwidthManagerTest.t.sol (L134-146)
```text
    /// 1e11 in 18-d is sub-microcent on a 6-d token — would scale to
    /// 0 raw, so the manager must reject before silently undercharging.
    function testRejectsNonRepresentablePrice() public {
        Stable6d usd = new Stable6d("USD Coin", "USDC");
        TestHost usdHost = _deployHost(address(usd));
        BandwidthManager usdMgr = new BandwidthManager(address(this));
        usdMgr.setHost(address(usdHost));
        _setTier(usdMgr, usdHost, 2, 1e11);

        vm.expectRevert(BandwidthManager.PriceNotRepresentable.selector);
        vm.prank(BUYER);
        usdMgr.purchase(APP, 2, 1, APP_CHAIN);
    }
```
