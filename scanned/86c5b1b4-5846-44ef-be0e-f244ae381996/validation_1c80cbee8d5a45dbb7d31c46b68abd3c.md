### Title
Nested Unbounded Loops in `_getTotalEthInProtocol()` Can Cause `updateRSETHPrice()` and Deposit Functions to Run Out of Gas - (File: contracts/LRTOracle.sol, contracts/NodeDelegator.sol, contracts/LRTDepositPool.sol)

### Summary
The public `updateRSETHPrice()` function and the user-facing `depositETH()`/`depositAsset()` functions both trigger a deeply nested loop chain: supported assets → NDCs → EigenLayer queued withdrawals → strategies. As the number of NDCs, supported assets, and queued withdrawals grows toward their configured maximums, these functions can exhaust the block gas limit, making them permanently uncallable.

### Finding Description
`LRTOracle.updateRSETHPrice()` calls `_getTotalEthInProtocol()`, which iterates over every supported asset and for each calls `ILRTDepositPool.getTotalAssetDeposits(asset)`. That in turn calls `getAssetDistributionData(asset)` (or `getETHDistributionData()`), which loops over every NDC in `nodeDelegatorQueue` and calls `INodeDelegator.getAssetUnstaking(asset)` on each one.

`NodeDelegator.getAssetUnstaking()` itself contains a **nested loop**: it fetches all queued withdrawals from EigenLayer via `_getDelegationManager().getQueuedWithdrawals(address(this))` and then iterates over every withdrawal and every strategy within each withdrawal.

The total work per `updateRSETHPrice()` call is:

```
supportedAssets.length × nodeDelegatorQueue.length × queuedWithdrawals_per_NDC × strategies_per_withdrawal
```

The same nested loop is triggered by `depositETH()`/`depositAsset()` via `_beforeDeposit()` → `_checkIfDepositAmountExceedesCurrentLimit()` → `getTotalAssetDeposits()`.

The protocol itself acknowledges this concern: the comment in `LRTUnstakingVault.setMaxUncompletedWithdrawalCount` states *"120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price"* and caps `maxUncompletedWithdrawalCount` at 80. However, `getAssetUnstaking` is called `supportedAssets.length × nodeDelegatorQueue.length` times (e.g., 3 assets × 10 NDCs = 30 external calls to EigenLayer), each returning and iterating over that NDC's full withdrawal queue. The cap on total withdrawals does not prevent the multiplicative gas cost of calling `getAssetUnstaking` once per asset per NDC.

### Impact Explanation
If the combined gas cost of the nested loops exceeds the block gas limit:
- `updateRSETHPrice()` becomes permanently uncallable → rsETH price is frozen at a stale value.
- `depositETH()` and `depositAsset()` revert on every call → user deposits are frozen.

This constitutes **temporary (potentially permanent) freezing of funds** and **unbounded gas consumption**.

### Likelihood Explanation
The protocol is designed to support up to `maxNodeDelegatorLimit` NDCs (default 10, admin-adjustable), multiple supported assets (currently ETH, stETH, ETHx), and up to 80 uncompleted withdrawals. At maximum configuration, `getAssetUnstaking` is called 30+ times per `updateRSETHPrice()` invocation, each making an external call to EigenLayer and iterating over nested arrays. Any unprivileged user calling `updateRSETHPrice()` or `depositETH()` triggers this path. No special permissions are required.

### Recommendation
Replace the per-asset, per-NDC call to `getAssetUnstaking` with a single batched query per NDC that returns all asset unstaking amounts in one pass, eliminating the outer asset loop. Alternatively, cache the result of `getQueuedWithdrawals` per NDC and reuse it across all asset queries within a single `getTotalAssetDeposits` call. Also enforce a strict upper bound on `nodeDelegatorQueue.length` and `supportedAssetList.length` to prevent the product of loop bounds from growing unboundedly.

### Proof of Concept

**Entry path (unprivileged):**

```
updateRSETHPrice()                          // LRTOracle.sol:87 — public, no auth
  └─ _getTotalEthInProtocol()               // LRTOracle.sol:331
       └─ for each asset in supportedAssets // LRTOracle.sol:336
            └─ getTotalAssetDeposits(asset) // LRTDepositPool.sol:385
                 └─ getAssetDistributionData(asset) // LRTDepositPool.sol:426
                      └─ for each NDC in nodeDelegatorQueue // LRTDepositPool.sol:447
                           └─ getAssetUnstaking(asset)  // NodeDelegator.sol:405
                                └─ getQueuedWithdrawals() // external EigenLayer call
                                └─ for each withdrawal    // NodeDelegator.sol:409
                                     └─ for each strategy // NodeDelegator.sol:412
```

**Same path via deposits (unprivileged):**

```
depositETH() / depositAsset()
  └─ _beforeDeposit()
       └─ _checkIfDepositAmountExceedesCurrentLimit()
            └─ getTotalAssetDeposits()
                 └─ [same nested loop chain as above]
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
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

**File:** contracts/LRTUnstakingVault.sol (L150-158)
```text
    function setMaxUncompletedWithdrawalCount(uint256 _maxUncompletedWithdrawalCount) external onlyLRTManager {
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;

        emit MaxUncompletedWithdrawalCountSet(_maxUncompletedWithdrawalCount);
```
