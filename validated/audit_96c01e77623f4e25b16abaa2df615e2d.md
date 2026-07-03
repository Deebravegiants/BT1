### Title
TVL Inflation via Direct Token Donation Blocks `updateRSETHPrice()`, Causing Stale rsETH Price - (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`)

### Summary

`LRTOracle._getTotalEthInProtocol()` computes the protocol's total ETH value using raw `balanceOf` and `address.balance` reads across `LRTDepositPool`, `NodeDelegator` contracts, and `LRTUnstakingVault`. Because these contracts accept direct ETH/token transfers from anyone, an unprivileged attacker can donate assets to artificially inflate `totalETHInProtocol`. This inflated value is fed directly into `_updateRsETHPrice()`, where it can trigger either `PriceAboveDailyThreshold` (blocking non-manager callers) or `DailyFeeMintLimitExceeded` (blocking all callers including the manager until the daily limit is adjusted). The result is a stale `rsETHPrice`, causing new depositors to receive more rsETH than they should, diluting existing holders.

### Finding Description

`LRTOracle._getTotalEthInProtocol()` iterates over all supported assets and calls `ILRTDepositPool.getTotalAssetDeposits(asset)`, which in turn calls `getAssetDistributionData()`:

For ERC20 LSTs:
```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);
assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);
```

For ETH:
```solidity
ethLyingInDepositPool = address(this).balance;
ethLyingInNDCs += nodeDelegatorQueue[i].balance;
ethLyingInUnstakingVault = lrtUnstakingVault.balance;
```

All of these are raw balance reads. `LRTDepositPool` has an open `receive()` function:
```solidity
receive() external payable { }
```

So any caller can send ETH directly to `LRTDepositPool` (or transfer LST tokens to any of the tracked contracts) to inflate `totalETHInProtocol`.

This inflated value flows into `_updateRsETHPrice()`:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

if (newRsETHPrice > highestRsethPrice) {
    bool isPriceIncreaseOffLimit =
        pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
    if (isPriceIncreaseOffLimit) {
        if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
            revert PriceAboveDailyThreshold();
        }
    }
}
```

And separately:
```solidity
uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
```

Where `_checkAndUpdateDailyFeeMintLimit` reverts with `DailyFeeMintLimitExceeded` if the computed fee rsETH amount exceeds `maxFeeMintAmountPerDay`. This revert path is hit by **both** `updateRSETHPrice()` and `updateRSETHPriceAsManager()`, since both call `_updateRsETHPrice()` internally.

### Impact Explanation

When `updateRSETHPrice()` is blocked:
- `rsETHPrice` stored in `LRTOracle` remains stale (lower than actual)
- New depositors calling `LRTDepositPool.depositETH()` or `depositAsset()` use `getRsETHAmountToMint()`, which divides by the stale `rsETHPrice`: `rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()`
- A lower stale `rsETHPrice` means new depositors receive **more rsETH than they should**, diluting existing rsETH holders' share of the protocol's TVL
- This constitutes theft of unclaimed yield from existing holders

If `DailyFeeMintLimitExceeded` is triggered, even `updateRSETHPriceAsManager()` reverts, requiring the manager to first call `setMaxFeeMintAmountPerDay()` before the price can be updated — a window during which the stale price persists.

**Impact:** Medium — Temporary freezing of unclaimed yield / dilution of existing rsETH holders.

### Likelihood Explanation

- Any unprivileged caller can send ETH directly to `LRTDepositPool` (open `receive()`) or transfer LST tokens to any tracked contract
- The donation required to exceed `pricePercentageLimit` is proportional to the current TVL (e.g., 1% of TVL if `pricePercentageLimit = 1e16`)
- The attacker permanently loses the donated assets, making this costly — however, a large rsETH holder partially recovers the cost because the donated assets increase the protocol's TVL, benefiting all rsETH holders proportionally
- The attack is repeatable: each time the manager updates the price, the attacker can donate again to re-trigger the block
- **Likelihood:** Low-Medium

### Recommendation

Replace raw `balanceOf` / `address.balance` reads with tracked internal accounting variables that are only updated through controlled deposit/transfer functions. This prevents untracked donations from inflating `totalETHInProtocol`. Alternatively, apply a TWAP or time-weighted smoothing to `totalETHInProtocol` before computing `newRsETHPrice`, analogous to the median-based fee approach recommended in the external report.

### Proof of Concept

1. Protocol state: TVL = 1000 ETH, rsETH supply = 950, `rsETHPrice` = ~1.052 ETH, `highestRsethPrice` = 1.052 ETH, `pricePercentageLimit` = 1% (1e16)
2. Attacker sends 11 ETH directly to `LRTDepositPool` via `address(lrtDepositPool).call{value: 11 ether}("")`
3. `totalETHInProtocol` is now 1011 ETH; `newRsETHPrice` = 1011/950 ≈ 1.064 ETH
4. `priceDifference` = 1.064 - 1.052 = 0.012 ETH > 1% × 1.052 = 0.01052 ETH → `isPriceIncreaseOffLimit = true`
5. Any non-manager call to `updateRSETHPrice()` reverts with `PriceAboveDailyThreshold`
6. `rsETHPrice` remains stale at 1.052 ETH
7. A new depositor deposits 10 ETH and receives `10 * 1e18 / 1.052e18 ≈ 9.506` rsETH instead of the correct `10 * 1e18 / 1.064e18 ≈ 9.398` rsETH — receiving ~1.1% more rsETH than they should, at the expense of existing holders

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTDepositPool.sol (L56-58)
```text
    //////////////////////////////////////////////////////////////*/

    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L444-461)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));

        uint256 ndcsCount = nodeDelegatorQueue.length;
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);

        assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
        assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);
```

**File:** contracts/LRTDepositPool.sol (L480-496)
```text
        ethLyingInDepositPool = address(this).balance;

        uint256 ndcsCount = nodeDelegatorQueue.length;

        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        ethLyingInUnstakingVault = lrtUnstakingVault.balance;
```

**File:** contracts/LRTDepositPool.sol (L516-520)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTOracle.sol (L197-210)
```text
    function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
        // Reset the period if it's unset or a day has passed
        if (block.timestamp >= feePeriodStartTime + 1 days) {
            currentPeriodMintedFeeAmount = 0;
            feePeriodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
    }
```

**File:** contracts/LRTOracle.sol (L249-266)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```
