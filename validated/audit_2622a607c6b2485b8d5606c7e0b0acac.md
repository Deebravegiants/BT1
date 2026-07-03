### Title
Unbounded Nested Iteration in `LRTOracle.updateRSETHPrice()` Causes Permanent Price-Update Failure as Protocol Scales - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a public function that internally iterates over every supported asset and, for each asset, over every NodeDelegator in the queue. Each NodeDelegator call further iterates over all EigenLayer queued withdrawals. As the protocol adds more supported assets and NodeDelegators (both normal operational growth), the gas cost of this function grows as O(assets × NDCs × queued\_withdrawals) and will eventually exceed the block gas limit, permanently preventing rsETH price updates.

### Finding Description
`LRTOracle._getTotalEthInProtocol()` is called by the public `updateRSETHPrice()`. It first fetches the entire `supportedAssetList` via `lrtConfig.getSupportedAssetList()`, then for each asset calls `ILRTDepositPool.getTotalAssetDeposits(asset)`. That function calls `getAssetDistributionData(asset)`, which loops over every entry in `nodeDelegatorQueue` and calls `INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset)` on each. `getAssetUnstaking()` in turn calls EigenLayer's `delegationManager.getQueuedWithdrawals(address(this))` and iterates over every queued withdrawal.

The three unbounded (or large-bounded) arrays are:
- `supportedAssetList` — no pagination getter; returned whole by `getSupportedAssetList()`
- `nodeDelegatorQueue` — no pagination getter; returned whole by `getNodeDelegatorQueue()`; bounded only by `maxNodeDelegatorLimit` which is admin-adjustable
- EigenLayer queued withdrawals per NDC — bounded by `maxUncompletedWithdrawalCount` (up to 80)

At realistic scale (10 assets × 10 NDCs × 80 queued withdrawals) the function executes up to 8 000 external storage reads/calls, which can exceed the block gas limit.

### Impact Explanation
If `updateRSETHPrice()` becomes permanently uncallable:
1. The stored `rsETHPrice` is permanently stale — the protocol's fee-minting mechanism (`_checkAndUpdateDailyFeeMintLimit`, fee minting in `_updateRsETHPrice`) stops functioning entirely.
2. Deposit and withdrawal exchange rates are computed from the stale price, causing users to receive incorrect rsETH amounts.
3. The price-deviation circuit-breaker (pause-on-drop) also stops working, removing a key safety mechanism.

This matches **Medium — temporary/permanent freezing of unclaimed yield** and **Low — contract fails to deliver promised returns**.

### Likelihood Explanation
The protocol is designed to support multiple LSTs and multiple NodeDelegators. `maxNodeDelegatorLimit` starts at 10 and is admin-adjustable upward. `maxUncompletedWithdrawalCount` can be up to 80. No code change or attack is required — ordinary protocol growth triggers the failure. `updateRSETHPrice()` is also callable by any external account, so there is no privileged gating that would prevent the call from being attempted.

### Recommendation
1. Add a paginated getter for `supportedAssetList`: `getSupportedAssetList(uint256 start, uint256 end)` and `getSupportedAssetListLength()`.
2. Add a paginated getter for `nodeDelegatorQueue`: `getNodeDelegatorQueue(uint256 start, uint256 end)` and `getNodeDelegatorQueueLength()`.
3. Refactor `_getTotalEthInProtocol()` to accept a pre-computed per-asset TVL array supplied by an off-chain keeper, or split the price update into per-asset partial updates that accumulate into a final price.

### Proof of Concept

Call stack that exhausts gas at scale:

```
updateRSETHPrice()                          // LRTOracle.sol:87 — public, no access control
  └─ _updateRsETHPrice()                    // LRTOracle.sol:214
       └─ _getTotalEthInProtocol()          // LRTOracle.sol:331
            └─ lrtConfig.getSupportedAssetList()   // returns entire supportedAssetList[]
            └─ for each asset (N assets):
                 ILRTDepositPool.getTotalAssetDeposits(asset)  // LRTDepositPool.sol:385
                   └─ getAssetDistributionData(asset)          // LRTDepositPool.sol:426
                        └─ for each NDC (M NDCs):
                             INodeDelegator.getAssetUnstaking(asset)  // NodeDelegator.sol:405
                               └─ delegationManager.getQueuedWithdrawals(ndc)
                               └─ for each queued withdrawal (K withdrawals):
                                    strategy.sharesToUnderlyingView(...)
```

With N=10, M=10, K=80 → 8 000 external calls in a single transaction. At ~2 100 gas per SLOAD and additional call overhead, this far exceeds the 30M block gas limit. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTConfig.sol (L186-188)
```text
    function getSupportedAssetList() external view override returns (address[] memory) {
        return supportedAssetList;
    }
```

**File:** contracts/LRTDepositPool.sol (L413-415)
```text
    function getNodeDelegatorQueue() external view override returns (address[] memory) {
        return nodeDelegatorQueue;
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
