Audit Report

## Title
Stale `rsETHPrice` Cache Enables Deposit-Then-Update Sandwich to Steal Accrued Yield - (File: contracts/LRTOracle.sol)

## Summary
`LRTOracle.rsETHPrice` is a cached state variable updated only when `updateRSETHPrice()` is explicitly called. Because `updateRSETHPrice()` is `public` and permissionless, an attacker can deposit at the stale (artificially low) price to receive excess rsETH, immediately trigger the price update themselves, then initiate a withdrawal at the now-correct higher price — extracting yield that belongs to existing rsETH holders.

## Finding Description
`rsETHPrice` is a stored value that only changes on an explicit call to `updateRSETHPrice()`, which is `public whenNotPaused` and callable by any address.

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

The deposit mint formula in `LRTDepositPool.getRsETHAmountToMint()` divides by the stale cached price:

```solidity
// contracts/LRTDepositPool.sol L519-521
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`getAssetPrice(asset)` reads a live Chainlink value; `rsETHPrice()` returns the stale cached value. As EigenLayer rewards accrue between `updateRSETHPrice()` calls, the true rsETH value rises above `rsETHPrice`. During this window the denominator is artificially low, so depositors receive more rsETH than fair value.

The withdrawal path in `LRTWithdrawalManager.getExpectedAssetAmount()` also uses `rsETHPrice`:

```solidity
// contracts/LRTWithdrawalManager.sol L593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

The `expectedAssetAmount` is locked in at `initiateWithdrawal` time and stored in the request. At `unlockQueue` time, `_calculatePayoutAmount` returns `min(request.expectedAssetAmount, currentReturn)`, so as long as the price does not fall below the stale price during the 8-day delay, the attacker receives the full `expectedAssetAmount` computed at the higher post-update price.

The `pricePercentageLimit` guard reverts non-manager callers only when the price jump exceeds the configured threshold. It does not prevent the attack when the staleness window produces a price increase within the allowed range, and it is configurable to zero (no limit).

## Impact Explanation
**High — Theft of unclaimed yield.** The attacker's excess rsETH dilutes all existing holders' proportional claim on protocol TVL. The profit is extracted directly from yield that should have accrued to existing depositors. The attack is repeatable every reward cycle and requires no special permissions.

## Likelihood Explanation
**Medium.** EigenLayer rewards accrue continuously, so a staleness window exists between every pair of `updateRSETHPrice()` calls. No special permissions are required: `updateRSETHPrice()` is public, deposits are open, and the attacker controls the timing of both the deposit and the price update. The `pricePercentageLimit` guard caps per-call profit but does not eliminate the attack — it only limits the price jump per invocation. When `pricePercentageLimit` is zero or the accrued yield is within the limit, the full attack executes without restriction.

## Recommendation
Call `_updateRsETHPrice()` (or an equivalent internal price refresh) atomically at the start of `depositAsset()` and `depositETH()` before computing `rsethAmountToMint`. This ensures every deposit uses the current, reward-inclusive price and eliminates the staleness window. Alternatively, compute the mint amount on-the-fly from live TVL rather than from a cached price variable.

## Proof of Concept

**Initial state:**
- `rsETHPrice = 1.000e18` (stale; true value is `1.010e18` due to accrued EigenLayer rewards)
- stETH/ETH Chainlink price = `1.000e18`
- Protocol has existing TVL (e.g., 1000 stETH from other depositors)

**Step 1 — Attacker calls `depositAsset(stETH, 100e18, ...)`:**
```
rsethAmountToMint = (100e18 * 1.000e18) / 1.000e18 = 100e18 rsETH
Fair amount       = (100e18 * 1.000e18) / 1.010e18 ≈  99.01e18 rsETH
Excess rsETH      ≈ 0.99e18 rsETH
```
`_beforeDeposit` → `getRsETHAmountToMint` uses stale `rsETHPrice = 1.000e18`.

**Step 2 — Attacker calls `updateRSETHPrice()`:**
- `_updateRsETHPrice()` computes true price from live Chainlink data via `_getTotalEthInProtocol()`
- `rsETHPrice` updates to `1.010e18` (within `pricePercentageLimit` or limit is zero)

**Step 3 — Attacker calls `initiateWithdrawal(stETH, 100e18, ...)`:**
```
expectedAssetAmount = 100e18 * 1.010e18 / 1.000e18 = 101e18 stETH
```
`getAvailableAssetAmount` passes because protocol TVL (≥1100 stETH) exceeds `assetsCommitted`.

**Step 4 — After `withdrawalDelayBlocks`, operator calls `unlockQueue`, attacker calls `completeWithdrawal`:**
- `_calculatePayoutAmount`: `currentReturn = 100e18 * 1.010e18 / 1.000e18 = 101e18`; `min(101e18, 101e18) = 101e18`
- Attacker receives **101 stETH**
- Net profit: **1 stETH** extracted from existing holders' accrued yield

**Foundry test sketch:**
```solidity
function test_stalePrice_yieldTheft() public fork {
    // 1. Confirm rsETHPrice is stale (< true TVL/supply)
    uint256 stalePriceBeforeUpdate = lrtOracle.rsETHPrice();
    // 2. Attacker deposits 100 stETH, records rsETH minted
    vm.prank(attacker);
    lrtDepositPool.depositAsset(stETH, 100e18, 0, "");
    uint256 rsETHMinted = rsETH.balanceOf(attacker);
    // 3. Attacker updates price
    vm.prank(attacker);
    lrtOracle.updateRSETHPrice();
    uint256 newPrice = lrtOracle.rsETHPrice();
    assertGt(newPrice, stalePriceBeforeUpdate);
    // 4. Attacker initiates withdrawal
    vm.prank(attacker);
    lrtWithdrawalManager.initiateWithdrawal(stETH, rsETHMinted, "");
    // 5. Advance blocks, operator unlocks, attacker completes
    vm.roll(block.number + withdrawalDelayBlocks + 1);
    operator.unlockQueue(stETH, ...);
    vm.prank(attacker);
    lrtWithdrawalManager.completeWithdrawal(stETH, "");
    // 6. Assert attacker received > 100 stETH
    assertGt(stETH.balanceOf(attacker), 100e18);
}
```