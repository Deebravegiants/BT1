Looking at the actual code to verify each claim in the submission.

Audit Report

## Title
Token Donation Inflates `getTotalAssetDeposits()` via Raw `balanceOf()`, Enabling Deposit-Limit DoS — (File: `contracts/LRTDepositPool.sol`)

## Summary
`getAssetDistributionData()` measures protocol-held LST balances using raw `IERC20(asset).balanceOf()` calls against `LRTDepositPool` and each registered NodeDelegator. Because ERC-20 transfers are permissionless, any holder of a supported LST can donate tokens directly to these addresses, inflating `getTotalAssetDeposits()`. The inflated total is consumed by `_checkIfDepositAmountExceedesCurrentLimit()`, which then reverts every subsequent `depositAsset()` call with `MaximumDepositLimitReached`. No sweep or recovery function exists in `LRTDepositPool` to eject unsolicited ERC-20 balances, so the DoS persists until privileged admin action, which the attacker can immediately counter by re-donating.

## Finding Description
`getAssetDistributionData()` computes the pool's LST holdings as:

```solidity
// LRTDepositPool.sol L444
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
// L448
assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);
```

Both reads include any tokens received via unsolicited `transfer()` calls. These values flow directly into `getTotalAssetDeposits()` (L385–397), which is consumed by `_checkIfDepositAmountExceedesCurrentLimit()`:

```solidity
// L676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This check is the sole gate in `_beforeDeposit()` (L661–663), called by both `depositAsset()` and `depositETH()`. Once a donation pushes `totalAssetDeposits` above `depositLimitByAsset`, the condition `totalAssetDeposits + amount > limit` is permanently true for any non-zero `amount`, blocking all deposits for that asset.

`LRTDepositPool` does not inherit `Recoverable` and contains no sweep or rescue function for ERC-20 tokens. The only privileged escape valve is `swapETHForAssetWithinDepositPool()` (operator-only), which requires the operator to supply ETH in exchange for the donated LST — an indirect and costly mitigation. Moving donated tokens to an NDC via `transferAssetToNodeDelegator()` provides no relief because NDC balances are also counted in `assetLyingInNDCs` (L448).

The same inflated `getTotalAssetDeposits()` value feeds `LRTOracle._getTotalEthInProtocol()` (L341–343), which can push `newRsETHPrice` above the `pricePercentageLimit` threshold, causing `updateRSETHPrice()` to revert for any non-manager caller (L252–265). Additionally, `LRTWithdrawalManager.getAvailableAssetAmount()` (L599–603) uses the inflated total, allowing `initiateWithdrawal()` to over-commit `assetsCommitted` beyond real vault liquidity (L170–173).

## Impact Explanation
**Medium — Temporary freezing of funds.** Once the donation pushes `totalAssetDeposits` above the configured cap, all `depositAsset()` calls for that LST revert with `MaximumDepositLimitReached`. Users' LST tokens are temporarily unable to enter the protocol. Because the donated tokens cannot be ejected without privileged operator action (and the attacker can immediately re-donate after each admin cap increase), the freeze is effectively continuous at low cost. Existing deposited funds remain withdrawable; the impact is on new inflows.

## Likelihood Explanation
**High.** The attack requires only holding a small amount of any supported LST (stETH, ETHx, sfrxETH, etc.) and calling `transfer()` on it. No special role, flash loan, or complex setup is needed. The cost equals the donated amount, which can be as small as 1 wei above the remaining deposit headroom. The attack is repeatable after every admin cap adjustment, making continuous DoS economically viable.

## Recommendation
Replace raw `balanceOf()` reads in `getAssetDistributionData()` with an internal accounting variable (e.g., `depositedBalance[asset]`) that is incremented exclusively inside `depositAsset()` and `transferAssetToNodeDelegator()` and decremented on outflows. This mirrors the ERC-4626 pattern of maintaining a separate `totalAssets` counter rather than relying on `balanceOf(address(this))`. Alternatively, add a privileged `sweepDonatedTokens()` function to `LRTDepositPool` that transfers any balance exceeding the internally tracked amount to the treasury, restoring the correct accounting without requiring a cap increase.

## Proof of Concept
1. Assume `depositLimitByAsset(stETH) = 10_000e18` and `getTotalAssetDeposits(stETH) = 9_999e18` (1 stETH headroom).
2. Attacker calls `stETH.transfer(address(lrtDepositPool), 2e18)`.
3. `getAssetDistributionData()` now returns `assetLyingInDepositPool` inflated by `2e18`, making `getTotalAssetDeposits(stETH) = 10_001e18`.
4. Any user calling `depositAsset(stETH, amount, ...)` triggers `_checkIfDepositAmountExceedesCurrentLimit()` → `10_001e18 + amount > 10_000e18` → `true` → revert `MaximumDepositLimitReached`.
5. Admin raises the cap to `10_003e18`; attacker immediately calls `stETH.transfer(address(lrtDepositPool), 3e18)`, restoring the DoS.
6. The donated stETH remains in the pool with no protocol mechanism to eject it without operator ETH expenditure.

**Foundry fork test outline:**
```solidity
function testDonationDoS() public fork {
    address pool = address(lrtDepositPool);
    uint256 limit = lrtConfig.depositLimitByAsset(stETH);
    uint256 current = pool.getTotalAssetDeposits(stETH);
    uint256 gap = limit - current + 1; // 1 wei above limit
    deal(stETH, attacker, gap);
    vm.prank(attacker);
    IERC20(stETH).transfer(pool, gap);
    vm.prank(user);
    vm.expectRevert(ILRTDepositPool.MaximumDepositLimitReached.selector);
    lrtDepositPool.depositAsset(stETH, 1e18, 0, "");
}
```