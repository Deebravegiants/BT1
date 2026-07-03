### Title
ETH Unstaking Shares Used Directly as ETH Amounts Without Conversion — (`contracts/NodeDelegator.sol`)

### Summary

In `NodeDelegator.getAssetUnstaking()`, queued withdrawal shares for LST strategies are correctly converted to underlying asset amounts via `strategy.sharesToUnderlyingView()`, but for the beacon chain ETH strategy, the raw shares are returned directly without any conversion. Since EigenLayer's post-PEPE beacon chain ETH strategy denominate shares in Gwei (1 share = 1 gwei), not Wei, this causes `getAssetUnstaking(ETH_TOKEN)` to return a value ~1e9× smaller than the actual ETH amount queued for unstaking.

### Finding Description

In `NodeDelegator.getAssetUnstaking()`, the code explicitly distinguishes between ETH and LST strategies:

```solidity
uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
amount += strategyAsset == LRTConstants.ETH_TOKEN
    ? sharesToUnstake                                    // shares used directly — no conversion
    : strategy.sharesToUnderlyingView(sharesToUnstake);  // correctly converts shares → assets
``` [1](#0-0) 

For LST strategies, `strategy.sharesToUnderlyingView(sharesToUnstake)` converts EigenLayer shares to the underlying token amount. For the beacon chain ETH strategy, the raw `sharesToUnstake` value (in Gwei) is returned as if it were Wei. This is the exact same class of bug as the external report: shares used where assets are expected.

This value propagates upward through the entire TVL accounting stack:

1. `getAssetUnstaking(ETH_TOKEN)` → returns Gwei instead of Wei
2. `LRTDepositPool.getETHDistributionData()` accumulates it as `ethUnstakingFromEigenLayer` [2](#0-1) 

3. `getTotalAssetDeposits(ETH_TOKEN)` sums all ETH components including this value [3](#0-2) 

4. `LRTOracle._getTotalEthInProtocol()` uses `getTotalAssetDeposits` to compute total protocol ETH [4](#0-3) 

5. `_updateRsETHPrice()` divides total ETH by rsETH supply to compute `rsETHPrice` [5](#0-4) 

### Impact Explanation

When ETH is queued for unstaking from EigenLayer (i.e., between `initiateUnstaking` and `completeUnstaking`), the protocol's reported total ETH is understated by approximately `(actual_ETH_unstaking * (1 - 1/1e9))`. This deflates `rsETHPrice`, causing every depositor to receive more rsETH than they should for their deposit — a direct theft of yield from existing rsETH holders. Conversely, withdrawers computing `getExpectedAssetAmount` via `rsETHPrice` receive less ETH than they are owed.

**Impact: High — theft of unclaimed yield / incorrect protocol accounting.**

### Likelihood Explanation

This is triggered any time the operator calls `initiateUnstaking` for ETH (beacon chain strategy) and there are pending queued withdrawals. This is a routine operational action. Any unprivileged depositor or withdrawer is affected by the resulting mispriced rsETH. No special conditions are required beyond normal protocol operation.

### Recommendation

Apply the same `sharesToUnderlyingView` conversion for ETH as is done for LSTs. For the beacon chain ETH strategy, call the strategy's conversion function rather than using raw shares:

```diff
- amount += strategyAsset == LRTConstants.ETH_TOKEN
-     ? sharesToUnstake
-     : strategy.sharesToUnderlyingView(sharesToUnstake);
+ amount += strategy.sharesToUnderlyingView(sharesToUnstake);
```

This mirrors the fix recommended in the external report: always convert shares to their underlying asset value before using them in accounting.

### Proof of Concept

1. Operator calls `initiateUnstaking` with the beacon chain ETH strategy and some shares (e.g., 32e9 shares representing 32 ETH).
2. `getAssetUnstaking(ETH_TOKEN)` is called — it returns `32e9` (Gwei) instead of `32e18` (Wei).
3. `LRTDepositPool.getTotalAssetDeposits(ETH_TOKEN)` is understated by `32e18 - 32e9 ≈ 32e18`.
4. `LRTOracle._getTotalEthInProtocol()` is understated by the same amount.
5. `rsETHPrice` is computed as `(totalETH - understated_amount) / rsethSupply`, yielding a deflated price.
6. A new depositor calling `depositETH` receives `rsethAmountToMint = (amount * assetPrice) / rsETHPrice` — since `rsETHPrice` is deflated, they receive more rsETH than they should, diluting existing holders. [6](#0-5)

### Citations

**File:** contracts/NodeDelegator.sol (L421-424)
```text
                uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
                amount += strategyAsset == LRTConstants.ETH_TOKEN
                    ? sharesToUnstake
                    : strategy.sharesToUnderlyingView(sharesToUnstake);
```

**File:** contracts/LRTDepositPool.sol (L394-396)
```text
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
```

**File:** contracts/LRTDepositPool.sol (L488-490)
```text
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L341-343)
```text
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
