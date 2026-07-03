### Title
Unbounded Gas Consumption in `updateRSETHPrice()` via Nested Loops Over NDCs and Queued EigenLayer Withdrawals — (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is publicly callable with no access control beyond `whenNotPaused`. Its internal call chain traverses nested loops whose depth scales with the number of supported assets, NodeDelegator contracts (NDCs), and EigenLayer queued withdrawals. As the protocol grows, this function's gas cost can exceed the block gas limit, permanently breaking the rsETH price update mechanism and causing the stored exchange rate to become stale.

### Finding Description
The public entry point `updateRSETHPrice()` calls `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`.

`_getTotalEthInProtocol()` iterates over every supported asset and calls `LRTDepositPool.getTotalAssetDeposits(asset)` for each: [1](#0-0) 

`getTotalAssetDeposits` dispatches to `getAssetDistributionData` (for LSTs) or `getETHDistributionData` (for ETH). Both functions loop over every NDC in `nodeDelegatorQueue` and call `NodeDelegator.getAssetUnstaking(asset)` on each: [2](#0-1) [3](#0-2) 

`getAssetUnstaking` calls EigenLayer's `getQueuedWithdrawals(address(this))` and then iterates over every returned withdrawal and every strategy within each withdrawal: [4](#0-3) 

The total work scales as **O(assets × NDCs × withdrawals × strategies)**. With 10 supported assets, 10 NDCs, and 80 queued withdrawals per NDC (the current cap), `getQueuedWithdrawals` is invoked 100 times and `sharesToUnderlyingView` is invoked up to tens of thousands of times. The protocol's own code comments acknowledge this ceiling: [5](#0-4) 

The cap of 80 (`maxUncompletedWithdrawalCount ≤ 80`) is a partial mitigation, but it does not account for:
- The multiplicative effect of iterating per-asset (each NDC's withdrawals are fetched once per supported asset, not once total).
- EigenLayer-side forced undelegations that add queued withdrawals outside the protocol's tracked count.
- Future increases to `maxNodeDelegatorLimit` (currently 10, but admin-settable) or the number of supported assets.

`updateRSETHPriceAsManager()` calls the same `_updateRsETHPrice()` path and is equally affected: [6](#0-5) 

### Impact Explanation
If `updateRSETHPrice()` reverts due to gas exhaustion, the stored `rsETHPrice` is never updated. Because rsETH is yield-bearing and its price monotonically increases, a stale price is lower than the true price. Users who deposit while the price is stale receive more rsETH than they are entitled to, diluting all existing rsETH holders. The protocol's fee-minting mechanism also stops functioning. This constitutes **unbounded gas consumption** (medium) with a secondary effect of **temporary freezing of the price update mechanism** (medium).

### Likelihood Explanation
The protocol explicitly acknowledges the gas ceiling in `LRTUnstakingVault.sol` (line 151–152). The current cap of 80 uncompleted withdrawals was chosen specifically to stay within the block gas limit. Any combination of: (a) admin increasing `maxNodeDelegatorLimit` beyond 10, (b) adding more supported assets, or (c) EigenLayer-side forced undelegations pushing the actual queued-withdrawal count above the protocol-tracked count, can push gas consumption past the 30 M gas block limit. This is a realistic operational scenario, not a theoretical one.

### Recommendation
Refactor `getAssetUnstaking` so that `getQueuedWithdrawals` is called **once per NDC** and the result is reused across all assets, rather than being fetched once per asset per NDC. Alternatively, introduce a dedicated view function in `NodeDelegatorHelper` that returns all asset unstaking amounts in a single pass over the queued withdrawals, and call it once per NDC inside `_getTotalEthInProtocol`.

### Proof of Concept
1. Protocol reaches: 10 supported assets, 10 NDCs, 80 queued withdrawals per NDC (all within current parameter bounds).
2. Any caller invokes `updateRSETHPrice()`.
3. `_getTotalEthInProtocol()` calls `getTotalAssetDeposits` 10 times (once per asset).
4. Each call iterates 10 NDCs and calls `getAssetUnstaking` per NDC → 100 calls to EigenLayer's `getQueuedWithdrawals`.
5. Each `getAssetUnstaking` iterates 80 withdrawals × N strategies, calling `sharesToUnderlyingView` per strategy.
6. Aggregate gas exceeds the 30 M block gas limit; the transaction reverts.
7. `rsETHPrice` is not updated; subsequent depositors receive inflated rsETH amounts at the stale (lower) price, diluting existing holders.

### Citations

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L336-348)
```text
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
```

**File:** contracts/LRTDepositPool.sol (L446-456)
```text
        uint256 ndcsCount = nodeDelegatorQueue.length;
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTDepositPool.sol (L482-493)
```text
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
```

**File:** contracts/NodeDelegator.sol (L405-427)
```text
    function getAssetUnstaking(address asset) external view returns (uint256 amount) {
        (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
            _getDelegationManager().getQueuedWithdrawals(address(this));

        for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
            IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];

            for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
                IStrategy strategy = withdrawal.strategies[strategyIndex];

                address strategyAsset = address(strategy) == address(lrtConfig.beaconChainETHStrategy())
                    ? LRTConstants.ETH_TOKEN
                    : address(strategy.underlyingToken());

                if (strategyAsset != asset) continue;

                uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
                amount += strategyAsset == LRTConstants.ETH_TOKEN
                    ? sharesToUnstake
                    : strategy.sharesToUnderlyingView(sharesToUnstake);
            }
        }
    }
```

**File:** contracts/LRTUnstakingVault.sol (L151-152)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
```
