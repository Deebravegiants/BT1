### Title
Unbounded Gas Growth in Deposit Path via Nested NDC and EigenLayer Withdrawal Iteration - (File: `contracts/LRTDepositPool.sol`)

### Summary
Every user deposit triggers a nested iteration over all NodeDelegators and their EigenLayer queued withdrawals. As the protocol scales (more NDCs, more pending unstaking operations), the gas cost of `depositETH()` and `depositAsset()` grows proportionally, eventually making deposits prohibitively expensive or reverting at the block gas limit.

### Finding Description

`depositETH()` and `depositAsset()` are the primary public entry points for any depositor. Both call `_beforeDeposit()` → `_checkIfDepositAmountExceedesCurrentLimit()` → `getTotalAssetDeposits()` → `getAssetDistributionData()` / `getETHDistributionData()`. [1](#0-0) 

`getAssetDistributionData()` iterates over the entire `nodeDelegatorQueue` array and for each NDC makes three external calls, including `INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset)`: [2](#0-1) 

`getETHDistributionData()` does the same for ETH: [3](#0-2) 

`getAssetUnstaking()` in `NodeDelegator.sol` calls `_getDelegationManager().getQueuedWithdrawals(address(this))` — an external call to EigenLayer — and then performs a **nested loop** over all returned queued withdrawals and their strategies: [4](#0-3) 

The total gas cost per deposit therefore scales as:

```
nodeDelegatorQueue.length × (3 external calls per NDC + queuedWithdrawals_per_NDC × strategies_per_withdrawal)
```

### Impact Explanation

As the protocol grows:
- `nodeDelegatorQueue` can grow up to `maxNodeDelegatorLimit` (admin-set, initially 10, can be raised without an upper bound check beyond the current queue length). [5](#0-4) 

- Each NDC accumulates queued EigenLayer withdrawals up to `maxUncompletedWithdrawalCount` (capped at 80 total across all NDCs). [6](#0-5) 

With 10 NDCs and 80 total queued withdrawals, each deposit already triggers 10 external `getQueuedWithdrawals()` calls to EigenLayer plus iteration over all returned withdrawal structs. If `maxNodeDelegatorLimit` is raised (e.g., to 20 or 30 as the protocol expands), the gas cost scales linearly. At sufficient scale, `depositETH()` and `depositAsset()` will revert due to the block gas limit, causing a **temporary freeze of user deposits** — a Medium impact per the allowed scope.

The protocol itself acknowledges this gas sensitivity in a comment in `LRTUnstakingVault.sol`: [7](#0-6) 

However, no analogous guard exists on the deposit path.

### Likelihood Explanation

This is triggered on **every** user deposit. The gas cost is not static — it grows monotonically as the protocol adds NDCs and queues more EigenLayer withdrawals. Both of these are expected operational activities. The likelihood increases over time as the protocol scales, making this a realistic medium-term DoS vector for the deposit function.

### Recommendation

Decouple the accounting of queued EigenLayer withdrawals from the hot deposit path. Options include:
- Maintain a cached/stored `assetUnstaking` value per NDC that is updated lazily (e.g., only when `initiateUnstaking` or `completeUnstaking` is called), rather than recomputing it on every deposit by querying EigenLayer.
- Separate `getTotalAssetDeposits()` into a view-only function not called during state-changing deposit operations, and use a stored TVL snapshot for deposit limit checks.

### Proof of Concept

1. Admin adds 10 NDCs to `nodeDelegatorQueue` (at `maxNodeDelegatorLimit = 10`).
2. Protocol queues 80 EigenLayer withdrawals across all NDCs (at `maxUncompletedWithdrawalCount = 80`), each with 2 strategies.
3. Any user calls `depositETH(1 ether, 0)`.
4. Execution path: `depositETH` → `_beforeDeposit` → `getTotalAssetDeposits` → `getETHDistributionData` → 10 iterations, each calling `getAssetUnstaking()` → 10 external `getQueuedWithdrawals()` calls to EigenLayer + iteration over ~8 withdrawal structs × 2 strategies per NDC.
5. If admin later raises `maxNodeDelegatorLimit` to 20 and queued withdrawals remain at 80, the gas cost doubles.
6. At sufficient scale, the transaction reverts with out-of-gas, blocking all new deposits. [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
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

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
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
