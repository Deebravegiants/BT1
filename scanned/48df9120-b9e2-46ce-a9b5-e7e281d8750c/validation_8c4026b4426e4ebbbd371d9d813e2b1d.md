### Title
Nested Unbounded Loop in `_getTotalEthInProtocol()` Can Permanently Freeze rsETH Price Updates - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle._getTotalEthInProtocol()` contains a deeply nested loop structure: it iterates over all supported assets, and for each asset calls `LRTDepositPool.getAssetDistributionData()`, which iterates over all NDCs, and for each NDC calls `NodeDelegator.getAssetUnstaking()`, which iterates over all EigenLayer queued withdrawals. As the protocol scales, this compound loop can exceed the block gas limit, permanently preventing `updateRSETHPrice()` from executing and freezing the rsETH price.

### Finding Description

`LRTOracle._getTotalEthInProtocol()` is called by the public `updateRSETHPrice()` function. Its gas cost is O(supportedAssets × NDCs × queuedWithdrawals × strategies_per_withdrawal):

**Level 1 — `_getTotalEthInProtocol()` loops over `supportedAssets`:** [1](#0-0) 

There is no hard cap on `supportedAssetList`. Assets are added via `LRTConfig.addNewSupportedAsset()` (TIME_LOCK_ROLE) with no upper bound enforced: [2](#0-1) 

**Level 2 — `getTotalAssetDeposits()` → `getAssetDistributionData()` loops over `nodeDelegatorQueue`:** [3](#0-2) 

`maxNodeDelegatorLimit` defaults to 10 and is admin-adjustable upward: [4](#0-3) 

**Level 3 — `getAssetUnstaking()` loops over all EigenLayer queued withdrawals:** [5](#0-4) 

Each queued withdrawal also contains an inner loop over `withdrawal.strategies`. The `maxUncompletedWithdrawalCount` is capped at 80 per NDC: [6](#0-5) 

**Compound gas cost:** With 10 supported assets, 10 NDCs, and 80 queued withdrawals each (all within configured limits), the innermost loop body executes up to 10 × 10 × 80 = 8,000 times, each making multiple external EigenLayer calls (`getQueuedWithdrawals`, `sharesToUnderlyingView`). This can easily exceed the 30M block gas limit.

### Impact Explanation

If `updateRSETHPrice()` runs out of gas, the rsETH price stored in `rsETHPrice` becomes permanently stale. All deposit and withdrawal pricing depends on this value:

- `depositETH()` / `depositAsset()` → `getRsETHAmountToMint()` → `lrtOracle.rsETHPrice()` — users receive wrong rsETH amounts.
- `initiateWithdrawal()` → `getExpectedAssetAmount()` → `lrtOracle.rsETHPrice()` — users receive wrong asset amounts.
- `updateRSETHPriceAsManager()` calls the same `_updateRsETHPrice()` → `_getTotalEthInProtocol()`, so even the manager path is blocked.

**Impact: Medium — Permanent freezing of the rsETH price update mechanism, causing incorrect pricing for all deposits and withdrawals.**

### Likelihood Explanation

The protocol is designed to scale: more LSTs can be added as supported assets (no cap), more NDCs can be added (admin-adjustable limit), and EigenLayer queued withdrawals accumulate during normal operations (up to 80 per NDC). As the protocol grows to its designed capacity, the gas cost of `updateRSETHPrice()` grows multiplicatively. This is a realistic operational scenario, not a theoretical edge case.

### Recommendation

1. Cache the `getQueuedWithdrawals` result or limit the number of strategies iterated in `getAssetUnstaking()`.
2. Introduce a hard cap on `supportedAssetList` length in `LRTConfig.addNewSupportedAsset()`.
3. Decouple the rsETH price computation from the full nested traversal — consider maintaining running totals updated incrementally on each deposit/withdrawal/unstaking event rather than recomputing from scratch on every `updateRSETHPrice()` call.
4. Alternatively, split `_getTotalEthInProtocol()` into paginated calls so no single transaction must traverse the full state.

### Proof of Concept

1. Governance adds 10 supported assets via `LRTConfig.addNewSupportedAsset()`.
2. Admin adds 10 NDCs via `LRTDepositPool.addNodeDelegatorContractToQueue()`.
3. Operators call `NodeDelegator.initiateUnstaking()` repeatedly until each NDC has 80 queued withdrawals (the maximum allowed by `maxUncompletedWithdrawalCount`).
4. Any caller invokes `LRTOracle.updateRSETHPrice()`.
5. The call traverses 10 assets × 10 NDCs × 80 withdrawals = 8,000 EigenLayer external calls and reverts with out-of-gas.
6. `rsETHPrice` is now permanently stale. All subsequent `depositETH()`, `depositAsset()`, and `initiateWithdrawal()` calls use the frozen price, mispricing all user interactions.

### Citations

**File:** contracts/LRTOracle.sol (L333-348)
```text
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
```

**File:** contracts/LRTConfig.sol (L99-118)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }

    /// @dev private function to add a new supported asset
    /// @param asset Asset address
    /// @param depositLimit Deposit limit for the asset
    function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
        UtilLib.checkNonZeroAddress(asset);
        if (depositLimit == 0) {
            revert InvalidDepositLimit();
        }
        if (isSupportedAsset[asset]) {
            revert AssetAlreadySupported();
        }
        isSupportedAsset[asset] = true;
        supportedAssetList.push(asset);
        depositLimitByAsset[asset] = depositLimit;
        emit AddedNewSupportedAsset(asset, depositLimit);
    }
```

**File:** contracts/LRTDepositPool.sol (L290-297)
```text
    function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
        if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
            revert InvalidMaximumNodeDelegatorLimit();
        }

        maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
        emit MaxNodeDelegatorLimitUpdated(maxNodeDelegatorLimit);
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

**File:** contracts/LRTUnstakingVault.sol (L153-158)
```text
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;

        emit MaxUncompletedWithdrawalCountSet(_maxUncompletedWithdrawalCount);
```
