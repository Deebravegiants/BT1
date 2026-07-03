### Title
Unbounded Nested Loop in `getAssetUnstaking()` Causes `updateRSETHPrice()` to Run OOG - (File: contracts/NodeDelegator.sol)

### Summary
`updateRSETHPrice()` is a public, permissionless function that internally calls `getAssetUnstaking()` on every NodeDelegator for every supported asset. `getAssetUnstaking()` fetches all queued EigenLayer withdrawals via `getQueuedWithdrawals()` and iterates over them with a nested loop. The total gas scales as O(numAssets × numNDCs × numQueuedWithdrawals × numStrategies), with each inner iteration making external calls. The protocol's own code comments confirm that at 120 uncompleted withdrawals, `updateRSETHPrice()` would run OOG.

### Finding Description
The call chain is:

```
updateRSETHPrice() [public, no access control]
  → _updateRsETHPrice()
    → _getTotalEthInProtocol()                          // loops over all supported assets
      → getTotalAssetDeposits(asset)                    // per asset
        → getAssetDistributionData(asset)               // loops over all NDCs
          → getAssetUnstaking(asset)                    // per NDC, per asset
            → getQueuedWithdrawals(address(this))       // external call to EigenLayer
              → nested loop over withdrawals × strategies
```

In `NodeDelegator.getAssetUnstaking()`:

```solidity
(IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
    _getDelegationManager().getQueuedWithdrawals(address(this));

for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
    for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
        // external call: strategy.sharesToUnderlyingView(sharesToUnstake)
    }
}
```

`getQueuedWithdrawals()` is called `numAssets × numNDCs` times redundantly — for a given NDC, the result is identical regardless of which asset is being queried, yet it is fetched once per asset. With 3 assets and 5 NDCs, this is 15 separate external calls to EigenLayer, each returning the full queued withdrawal array and triggering the nested loop.

The protocol's own comment in `LRTUnstakingVault.sol` explicitly acknowledges the OOG risk:

```solidity
// 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
// Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
if (_maxUncompletedWithdrawalCount > 80) {
    revert MaxUncompletedWithdrawalCountTooHigh();
}
```

The cap of 80 is a soft mitigation. EigenLayer operators can force-undelegate NDCs (a standard EigenLayer mechanism, not a compromise), which creates additional queued withdrawals outside the protocol's tracking. The `setUncompletedWithdrawalCount()` function exists precisely to resync the counter after such events, but by then `updateRSETHPrice()` may already be OOG-ing.

### Impact Explanation
If `updateRSETHPrice()` runs OOG, the rsETH price cannot be updated. Since the rsETH price is required for:
- Minting rsETH on deposit (`getRsETHAmountToMint()` uses `lrtOracle.rsETHPrice()`)
- Unlocking withdrawal requests (`_unlockWithdrawalRequests` uses the oracle price)

A sustained OOG condition temporarily freezes both deposits and withdrawal unlocking — a **temporary freezing of funds** (Medium impact).

### Likelihood Explanation
The protocol operates on Ethereum mainnet where gas limits are ~30M per block. The team's own comment confirms 120 uncompleted withdrawals causes OOG. EigenLayer forced undelegations (triggered by EigenLayer's slashing/undelegation mechanism) can push the count above 80 without any LRT-rsETH admin action. Additionally, the redundant `getQueuedWithdrawals()` calls (once per asset per NDC) multiply the gas cost by `numAssets`, making the effective OOG threshold lower than the raw withdrawal count suggests.

### Recommendation
1. Cache `getQueuedWithdrawals()` per NDC and reuse the result across all assets, eliminating the `numAssets`-fold redundancy.
2. Refactor `getAssetUnstaking()` to accept pre-fetched withdrawal data rather than re-querying EigenLayer.
3. Consider computing `assetUnstakingFromEigenLayer` in a single pass over all NDCs and all assets simultaneously, rather than per-asset per-NDC.

### Proof of Concept
With 3 supported assets (ETH, stETH, ETHx), 5 NDCs, and 80 total uncompleted withdrawals (16 per NDC, 2 strategies each):

- `getQueuedWithdrawals()` is called: 3 assets × 5 NDCs = **15 times**
- Inner loop iterations: 15 × 16 withdrawals × 2 strategies = **480 iterations**, each with an external `sharesToUnderlyingView()` call
- At ~30k gas per external call: 480 × 30,000 = **14.4M gas** just for the inner loops, before accounting for EigenLayer's own `getQueuedWithdrawals()` overhead

If forced undelegations push the count to 120 (as the team's comment acknowledges as the OOG threshold), the gas exceeds the block limit and `updateRSETHPrice()` becomes permanently uncallable until withdrawals are completed.

**Affected code:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** contracts/LRTUnstakingVault.sol (L151-155)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
```
