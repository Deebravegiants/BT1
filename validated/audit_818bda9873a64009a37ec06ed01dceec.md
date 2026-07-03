Audit Report

## Title
Stale `highestRsethPrice` Not Reset on Asset Removal Enables Permissionless Protocol Freeze - (File: `contracts/LRTOracle.sol`)

## Summary
When `LRTConfig.removeSupportedAsset()` removes an asset, `LRTOracle.highestRsethPrice` is not reset to reflect the post-removal TVL. Because `updateRSETHPrice()` is a public, permissionless function, any caller can invoke it after the removal to compute a lower `newRsETHPrice` against the stale peak, triggering the downside protection branch that pauses `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle`, freezing all user deposits and withdrawals.

## Finding Description
`LRTConfig.removeSupportedAsset()` enforces that the removed asset's deposits do not exceed `maxNegligibleAmount`, but it makes no call into `LRTOracle` to update `highestRsethPrice`. [1](#0-0) 

After removal, `_getTotalEthInProtocol()` no longer counts the removed asset's TVL, so the next `_updateRsETHPrice()` call computes a lower `newRsETHPrice`. The downside protection branch then compares this lower price against the stale `highestRsethPrice`: [2](#0-1) 

If `diff > pricePercentageLimit.mulWad(highestRsethPrice)`, the function pauses `lrtDepositPool`, `withdrawalManager`, and `LRTOracle` and returns without updating `rsETHPrice`. Critically, the downside path has **no manager bypass** — unlike the upside path (line 263), which allows a manager to override the threshold, the downside path unconditionally pauses. This means even `updateRSETHPriceAsManager()` cannot update the price post-removal without triggering the freeze. [3](#0-2) 

The `maxNegligibleAmount` guard limits the per-removal TVL drop, but does not prevent the freeze in two realistic scenarios:

1. **Price already near threshold**: If `rsETHPrice` has drifted to within `pricePercentageLimit` of `highestRsethPrice` (e.g., due to prior slashing), even removing an asset with deposits well below `maxNegligibleAmount` can push the computed price over the threshold.
2. **Non-trivial `maxNegligibleAmount`**: If `maxNegligibleAmount` is set to a value that represents a meaningful fraction of total TVL (e.g., 10 ETH removed from a 100 ETH protocol with a 5% limit), the removal alone causes a price drop exceeding the limit.

The secondary issue — `assetPriceOracle[asset]` not being cleared — is a real but lower-severity concern. `updatePriceOracleFor` permits clearing the oracle for unsupported assets (the `checkNonZeroAddress` guard is skipped when `isSupportedAsset(asset)` is false), but this requires an explicit admin action that is not enforced. [4](#0-3) 

## Impact Explanation
**Medium — Temporary freezing of funds.** All user deposits and withdrawals are blocked until an admin manually unpauses each contract. The freeze is triggered by a public, zero-privilege function call (`updateRSETHPrice()`) after a legitimate admin asset-removal operation. The impact is concrete and matches the allowed scope.

## Likelihood Explanation
Asset removal is a documented, expected admin operation. `updateRSETHPrice()` is public with no access control. The two triggering scenarios (price near threshold, or non-trivial `maxNegligibleAmount`) are realistic in a live protocol. No attacker capability beyond calling a public function is required once the admin has removed the asset. The freeze is repeatable until an admin unpauses and resets the high-water mark.

## Recommendation
1. In `LRTOracle`, add an `onlyLRTAdmin`-restricted `resetHighestRsethPrice()` function that sets `highestRsethPrice` to the current `rsETHPrice`, to be called as part of the asset-removal workflow before `updateRSETHPrice()` is publicly invokable.
2. Add a manager bypass to the downside protection branch (mirroring the upside bypass at line 263) so that `updateRSETHPriceAsManager()` can update the price post-removal without triggering the pause.
3. Optionally, have `removeSupportedAsset()` call `ILRTOracle(oracle).updatePriceOracleFor(asset, address(0))` to clear the stale oracle entry atomically.

## Proof of Concept
1. Deploy with two assets (stETH, ETHx). rsETH price = 1.10 ETH. `highestRsethPrice = 1.10e18`. `pricePercentageLimit = 5e16` (5%). `maxNegligibleAmount = 50 ether`.
2. stETH deposits = 40 ETH (within `maxNegligibleAmount`). Total TVL = 1000 ETH. Admin calls `LRTConfig.removeSupportedAsset(stETH, idx)`. Succeeds. `highestRsethPrice` remains `1.10e18`.
3. `_getTotalEthInProtocol()` now returns 960 ETH. New rsETH price ≈ `1.10 * (960/1000)` = `1.056e18`. Diff from peak = `0.044e18`. `pricePercentageLimit.mulWad(1.10e18)` = `0.055e18`. `0.044e18 < 0.055e18` — no pause yet.
4. Alternatively, set `maxNegligibleAmount = 100 ether`, stETH deposits = 100 ETH. New price ≈ `1.10 * (900/1000)` = `0.99e18`. Diff = `0.11e18 > 0.055e18`. `isPriceDecreaseOffLimit = true`.
5. Any address calls `LRTOracle.updateRSETHPrice()`. `lrtDepositPool.pause()`, `withdrawalManager.pause()`, `_pause()` are all called. All deposits and withdrawals frozen.
6. `updateRSETHPriceAsManager()` also triggers the same pause — no privileged escape path exists for the downside branch.

### Citations

**File:** contracts/LRTConfig.sol (L80-93)
```text
        address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);

        if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
            revert CannotRemoveAssetWithDeposits(asset);
        }

        delete isSupportedAsset[asset];
        delete assetStrategy[asset];
        depositLimitByAsset[asset] = 0;

        supportedAssetList[tokenIndex] = supportedAssetList[supportedAssetList.length - 1];
        supportedAssetList.pop();

        emit RemovedSupportedAsset(asset);
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L113-119)
```text
    function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
        if (lrtConfig.isSupportedAsset(asset)) {
            UtilLib.checkNonZeroAddress(priceOracle);
        }
        assetPriceOracle[asset] = priceOracle;
        emit AssetPriceOracleUpdate(asset, priceOracle);
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```
