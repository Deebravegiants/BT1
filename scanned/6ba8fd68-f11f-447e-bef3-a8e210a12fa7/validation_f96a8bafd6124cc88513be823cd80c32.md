### Title
Unbounded Gas Consumption in Publicly Callable `updateRSETHPrice()` via Nested External Loops - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a public, permissionless function that triggers a deeply nested chain of external calls proportional to the number of supported assets, node delegators, and queued EigenLayer withdrawals. Any unprivileged caller can invoke it, and at maximum protocol configuration the cumulative gas cost can render the function uncallable, permanently freezing the price oracle and causing all subsequent deposits and withdrawals to operate on a stale rsETH price.

### Finding Description
`LRTOracle.updateRSETHPrice()` carries only a `whenNotPaused` guard — no role restriction — making it callable by any external account. [1](#0-0) 

Internally it calls `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`. [2](#0-1) 

`_getTotalEthInProtocol()` iterates over every entry in `supportedAssetList` and, for each asset, calls `ILRTDepositPool.getTotalAssetDeposits(asset)`. [3](#0-2) 

`getTotalAssetDeposits()` delegates to `getAssetDistributionData()`, which iterates over every entry in `nodeDelegatorQueue` (up to `maxNodeDelegatorLimit`, initialized to 10) and, for each NDC, makes three external calls — including `INodeDelegator.getAssetUnstaking(asset)`. [4](#0-3) 

`getAssetUnstaking()` in `NodeDelegator` calls EigenLayer's `DelegationManager.getQueuedWithdrawals(address(this))`, which returns all pending withdrawals for that NDC, and then iterates over every withdrawal and every strategy within each withdrawal. [5](#0-4) 

The total gas cost is therefore **O(assets × NDCs × queued\_withdrawals\_per\_NDC × strategies\_per\_withdrawal)**, with all four dimensions growing independently under normal protocol operation. `maxUncompletedWithdrawalCount` is capped at 80 total across all NDCs by `LRTUnstakingVault.setMaxUncompletedWithdrawalCount()`. [6](#0-5) 

At maximum configuration (4 supported assets × 10 NDCs × 80 queued withdrawals × multiple strategies each), the function executes hundreds of cross-contract calls in a single transaction, each consuming thousands of gas units.

### Impact Explanation
If the cumulative gas cost of `updateRSETHPrice()` approaches or exceeds the block gas limit (~30 M gas on Ethereum mainnet), the function becomes permanently uncallable. The stored `rsETHPrice` then becomes stale. Because `depositETH`, `depositAsset`, `initiateWithdrawal`, and `instantWithdrawal` all read `lrtOracle.rsETHPrice()` directly from storage without triggering an update, all user-facing operations continue to execute against the frozen, incorrect price. This constitutes a **medium-severity temporary (or permanent) freeze of the price-update mechanism**, causing the contract to fail to deliver promised returns and potentially enabling value extraction by users who observe the price divergence.

### Likelihood Explanation
The protocol is designed to scale: new assets can be added via governance (`addNewSupportedAsset`), new NDCs can be added by admin (`addNodeDelegatorContractToQueue`), and EigenLayer queued withdrawals accumulate during normal unstaking operations. As the protocol grows toward its configured limits, the gas cost of `updateRSETHPrice()` grows deterministically. No attacker action is required — ordinary protocol growth is sufficient to trigger the condition. Any user can then call the function and observe the revert, confirming the freeze.

### Recommendation
1. Restrict `updateRSETHPrice()` to a privileged role (e.g., `MANAGER` or a dedicated keeper role), consistent with the existing `updateRSETHPriceAsManager()` pattern, so that only trusted callers bear the gas cost and the function is not a public griefing surface.
2. Cache or lazily compute `getAssetUnstaking()` results rather than re-fetching all EigenLayer queued withdrawals on every price update call.
3. Consider breaking `_getTotalEthInProtocol()` into per-asset incremental updates stored in a mapping, so each call touches only one asset's NDC loop rather than all assets simultaneously.

### Proof of Concept
Call chain triggered by any unprivileged EOA:

```
attacker → LRTOracle.updateRSETHPrice()          [public, no role check]
  → _updateRsETHPrice()
    → _getTotalEthInProtocol()
      for each asset in supportedAssetList (N assets):          // LRTOracle.sol:336
        → LRTDepositPool.getTotalAssetDeposits(asset)           // LRTOracle.sol:341
          → getAssetDistributionData(asset)
            for each NDC in nodeDelegatorQueue (M NDCs):        // LRTDepositPool.sol:447
              → NodeDelegator.getAssetUnstaking(asset)          // LRTDepositPool.sol:451
                → DelegationManager.getQueuedWithdrawals(NDC)   // NodeDelegator.sol:406-407
                  for each withdrawal (W withdrawals):          // NodeDelegator.sol:409
                    for each strategy (S strategies):           // NodeDelegator.sol:412
                      → strategy.sharesToUnderlyingView(shares) // NodeDelegator.sol:424
```

At N=4, M=10, W=8 per NDC (80 total), S=2 strategies per withdrawal:
- Total `sharesToUnderlyingView` external calls: 4 × 10 × 8 × 2 = **640 external calls**
- Plus 40 `getQueuedWithdrawals` calls, 40 `getAssetBalance` calls, 40 `balanceOf` calls
- Total external calls per `updateRSETHPrice()` invocation: **>760**, each costing thousands of gas units, easily reaching tens of millions of gas. [1](#0-0) [7](#0-6) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L231-232)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

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
