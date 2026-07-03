### Title
Unbounded Nested Loop in `updateRSETHPrice()` Can Cause Permanent DOS of Price Updates - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a public function with no access control. Its internal call chain traverses a nested loop over all supported assets, all node delegators, and all EigenLayer queued withdrawals per delegator. The `supportedAssetList` has no explicit cap, and the multiplicative gas cost of this nested traversal can grow to exceed the block gas limit as the protocol scales, permanently preventing price updates.

### Finding Description

`LRTOracle.updateRSETHPrice()` is callable by any address: [1](#0-0) 

It delegates to `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`: [2](#0-1) 

This function loops over every entry in `supportedAssetList` — an array with **no explicit maximum length** — and for each asset calls `ILRTDepositPool.getTotalAssetDeposits(asset)`: [3](#0-2) 

`getTotalAssetDeposits()` calls `getAssetDistributionData()`, which itself loops over the entire `nodeDelegatorQueue`: [4](#0-3) 

For each NDC in that inner loop, `getAssetUnstaking()` is called on `NodeDelegator`, which fetches **all** queued withdrawals from EigenLayer's `DelegationManager` and iterates over them with a further nested loop over strategies per withdrawal: [5](#0-4) 

The total gas cost is therefore **O(assets × NDCs × queued_withdrawals × strategies_per_withdrawal)** — a four-dimensional product of external calls. The `supportedAssetList` in `LRTConfig` has no enforced cap: [6](#0-5) 

While `nodeDelegatorQueue` is capped at `maxNodeDelegatorLimit` (default 10) and `maxUncompletedWithdrawalCount` is capped at 80, the protocol's own comment acknowledges the gas sensitivity: [7](#0-6) 

As the protocol legitimately adds more supported LST assets over time, the outer loop in `_getTotalEthInProtocol()` grows, and the multiplicative cost of the full nested traversal can push `updateRSETHPrice()` past the block gas limit.

### Impact Explanation

If `updateRSETHPrice()` permanently reverts due to out-of-gas:

1. The stored `rsETHPrice` becomes permanently stale.
2. Protocol fee minting (which occurs inside `_updateRsETHPrice()`) stops entirely — theft of unclaimed yield.
3. The downside price-protection mechanism (auto-pause on large price drops) stops functioning.
4. `updateRSETHPriceAsManager()` (manager-only) calls the same `_updateRsETHPrice()` and would also revert.

**Impact: Medium — Unbounded gas consumption / Permanent freezing of unclaimed yield (protocol fees).**

### Likelihood Explanation

The `supportedAssetList` is extended via `addNewSupportedAsset()` gated by `TIME_LOCK_ROLE`, a legitimate governance path. As Kelp DAO expands to support additional LSTs (a stated protocol goal), the outer loop grows. Combined with the maximum allowed NDC count (10) and queued withdrawal count (80), even a modest increase in supported assets (e.g., 15–20) combined with a full NDC queue and near-maximum queued withdrawals can push the function past the ~30M gas block limit given the multiple external calls per iteration.

**Likelihood: Low** — requires the protocol to reach a specific combination of asset count, NDC count, and queued withdrawal count simultaneously.

### Recommendation

1. Cache and store the total ETH value incrementally (update per-asset totals on deposit/withdrawal events) rather than recomputing the full sum on every `updateRSETHPrice()` call.
2. Enforce an explicit maximum on `supportedAssetList` length in `_addNewSupportedAsset()`.
3. Alternatively, split `_getTotalEthInProtocol()` into a paginated or per-asset update pattern so no single transaction must traverse the full cross-product.

### Proof of Concept

Call path triggered by any unprivileged address:

```
updateRSETHPrice()                          // public, no access control
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for each asset in supportedAssetList (no cap):
                 └─ LRTDepositPool.getTotalAssetDeposits(asset)
                      └─ getAssetDistributionData(asset)
                           └─ for each NDC in nodeDelegatorQueue (≤10):
                                └─ NodeDelegator.getAssetUnstaking(asset)
                                     └─ DelegationManager.getQueuedWithdrawals()  // external call
                                          └─ for each withdrawal (≤80):
                                               └─ for each strategy in withdrawal:
                                                    └─ strategy.sharesToUnderlyingView()  // external call
```

With 15 supported assets × 10 NDCs × 80 withdrawals × 3 strategies = **36,000 iterations**, each involving external calls, the transaction will exceed the block gas limit, causing every subsequent call to `updateRSETHPrice()` to revert permanently.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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

**File:** contracts/NodeDelegator.sol (L406-427)
```text
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

**File:** contracts/LRTConfig.sol (L99-101)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }
```

**File:** contracts/LRTUnstakingVault.sol (L151-155)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
```
