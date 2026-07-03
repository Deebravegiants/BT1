### Title
Unbounded Gas Consumption in `getAssetUnstaking` Nested Loop Blocks Deposits - (File: `contracts/NodeDelegator.sol`)

### Summary

`depositETH` and `depositAsset` call `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit` → `getTotalAssetDeposits` → `getAssetDistributionData` / `getETHDistributionData`, which loops over every NDC and calls `getAssetUnstaking`. That function issues one `getQueuedWithdrawals()` external call per NDC and then iterates over every `(withdrawal, strategy)` pair, calling `strategy.sharesToUnderlyingView()` for each match. The total work is `NDC_count × withdrawals_per_NDC × strategies_per_withdrawal` external calls, all inside a state-changing transaction.

### Finding Description

**Exact call chain:**

```
depositETH / depositAsset
  └─ _beforeDeposit                                    [LRTDepositPool.sol:648]
       └─ _checkIfDepositAmountExceedesCurrentLimit    [LRTDepositPool.sol:676]
            └─ getTotalAssetDeposits                   [LRTDepositPool.sol:385]
                 └─ getAssetDistributionData /
                    getETHDistributionData             [LRTDepositPool.sol:447-456 / 484-492]
                         └─ INodeDelegator.getAssetUnstaking (per NDC)
                              └─ getQueuedWithdrawals() [external, EigenLayer]
                                   └─ strategy.sharesToUnderlyingView()
                                        per (withdrawal × strategy) pair
``` [1](#0-0) [2](#0-1) 

**Bounding parameters:**

| Parameter | Cap | Source |
|---|---|---|
| `maxUncompletedWithdrawalCount` | hard-capped at **80** | `LRTUnstakingVault.sol:153` |
| `maxNodeDelegatorLimit` | **no hard cap** (admin-settable) | `LRTDepositPool.sol:290-297` |
| strategies per withdrawal | bounded by supported assets (~5–10) | `initiateUnstaking` validation | [3](#0-2) [4](#0-3) 

**Gas arithmetic at current caps (80 withdrawals, 10 NDCs, 5 strategies):**

- 10 × `getQueuedWithdrawals()` external calls: ~10 × 10,000 gas = 100,000 gas
- 80 × 5 = 400 `sharesToUnderlyingView()` external calls: ~400 × 5,000 gas = 2,000,000 gas
- EigenLayer storage reads for 80 withdrawals (cold SLOADs): ~80 × 5 × 2,100 = 840,000 gas
- **Total: ~3–5M gas per deposit** at maximum allowed queue depth

Because `maxNodeDelegatorLimit` has no hard cap, an admin can register hundreds of NDCs. With N NDCs, the `getQueuedWithdrawals()` overhead alone scales as O(N) even when most NDCs have zero withdrawals, making the gas cost grow without a protocol-enforced ceiling. [5](#0-4) 

### Impact Explanation

Every user deposit (`depositETH` / `depositAsset`) must pay the full iteration cost. At maximum queue depth (80 withdrawals × 5 strategies × 10 NDCs), a deposit costs ~3–5M gas instead of the ~100–200k gas a user would expect. If `maxNodeDelegatorLimit` is raised (no hard cap), the per-NDC `getQueuedWithdrawals()` overhead scales linearly, eventually making deposits economically infeasible or causing OOG reverts for callers who set a reasonable gas limit. This matches **Medium: Unbounded gas consumption**.

The "permanently blocking" framing in the question is overstated at current caps (80 withdrawals, 10 NDCs stay within the 30M block gas limit), but the gas cost is already ~20–50× higher than expected and grows without a protocol-enforced ceiling on NDC count.

### Likelihood Explanation

The condition is reachable through normal operator activity: operators call `initiateUnstaking` with multi-strategy batches until `uncompletedWithdrawalCount` reaches `maxUncompletedWithdrawalCount`. No admin compromise is required to reach the 80-withdrawal maximum. The NDC count growing over time is also a normal operational expectation. [6](#0-5) 

### Recommendation

1. **Cache `getQueuedWithdrawals()` results**: Call it once per NDC and reuse the result for all assets, rather than once per `getAssetUnstaking(asset)` call per asset per NDC.
2. **Maintain an on-chain running total**: Track `assetUnstaking[asset]` as a storage variable updated on `initiateUnstaking` / `completeUnstaking`, eliminating the need to iterate EigenLayer's queue on every deposit.
3. **Add a hard cap on `maxNodeDelegatorLimit`**: Prevent unbounded growth of the per-NDC overhead.
4. **Separate the accounting view from the deposit hot path**: `getTotalAssetDeposits` should read from a cached/snapshotted value rather than recomputing from EigenLayer state on every transaction.

### Proof of Concept

```solidity
// Fork test outline (Foundry)
function test_depositOOG_atMaxWithdrawals() public {
    // 1. Deploy protocol on mainnet fork
    // 2. Fill each of the 10 NDCs with initiateUnstaking calls
    //    using multi-strategy batches until uncompletedWithdrawalCount == 80
    for (uint i = 0; i < 10; i++) {
        for (uint j = 0; j < 8; j++) {
            // each call: strategies = [stETH_strategy, ethx_strategy, ...] (5 strategies)
            vm.prank(operator);
            nodeDelegators[i].initiateUnstaking(fiveStrategies, fiveShares);
        }
    }
    // 3. Measure gas for a deposit
    uint256 gasBefore = gasleft();
    vm.prank(user);
    lrtDepositPool.depositETH{value: 1 ether}(0, "");
    uint256 gasUsed = gasBefore - gasleft();
    // Assert gas used is >> 1M (demonstrating the O(NDC × withdrawals × strategies) cost)
    assertGt(gasUsed, 2_000_000);
}
``` [7](#0-6) [8](#0-7) [2](#0-1)

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

**File:** contracts/LRTDepositPool.sol (L302-323)
```text
    function addNodeDelegatorContractToQueue(address[] calldata nodeDelegatorContracts) external onlyLRTAdmin {
        uint256 length = nodeDelegatorContracts.length;
        if (nodeDelegatorQueue.length + length > maxNodeDelegatorLimit) {
            revert MaximumNodeDelegatorLimitReached();
        }

        for (uint256 i; i < length;) {
            UtilLib.checkNonZeroAddress(nodeDelegatorContracts[i]);

            // check if node delegator contract is already added and add it if not
            if (isNodeDelegator[nodeDelegatorContracts[i]] == 0) {
                nodeDelegatorQueue.push(nodeDelegatorContracts[i]);
                emit NodeDelegatorAddedinQueue(nodeDelegatorContracts[i]);
            }

            isNodeDelegator[nodeDelegatorContracts[i]] = 1;

            unchecked {
                ++i;
            }
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L447-456)
```text
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```

**File:** contracts/NodeDelegator.sol (L304-330)
```text
        if (_getUnstakingVault().uncompletedWithdrawalCount() >= _getUnstakingVault().maxUncompletedWithdrawalCount()) {
            revert MaxUncompletedWithdrawalsReached();
        }
        if (strategies.length == 0) {
            revert ZeroLengthArray();
        }

        if (strategies.length != shares.length) {
            revert ArrayLengthMismatch();
        }

        for (uint256 i = 0; i < strategies.length; i++) {
            if (!NodeDelegatorHelper.isSupportedStrategy(lrtConfig, strategies[i])) {
                revert StrategyIsNotSetForAsset();
            }
        }

        IDelegationManager.QueuedWithdrawalParams[] memory queuedWithdrawalParams =
            new IDelegationManager.QueuedWithdrawalParams[](1);
        queuedWithdrawalParams[0] = IDelegationManagerTypes.QueuedWithdrawalParams({
            strategies: strategies, depositShares: shares, withdrawer: address(this)
        });

        bytes32[] memory withdrawalRoots = _getDelegationManager().queueWithdrawals(queuedWithdrawalParams);
        withdrawalRoot = withdrawalRoots[0];
        _getUnstakingVault().increaseUncompletedWithdrawalCount();
        emit WithdrawalQueued(_getNonce() - 1, address(this), withdrawalRoots);
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

**File:** contracts/LRTUnstakingVault.sol (L151-156)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;
```
