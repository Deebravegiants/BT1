### Title
Unbounded Nested-Loop Gas Consumption in `updateRSETHPrice()` Can Permanently Stale rsETH Price - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a permissionless public function that internally executes deeply nested loops across supported assets, node delegators, and EigenLayer queued withdrawals. As the protocol scales, the cumulative gas cost of these nested external calls can exceed the block gas limit, permanently preventing price updates and causing the rsETH exchange rate to become stale.

### Finding Description
`LRTOracle.updateRSETHPrice()` is callable by any address with no access restriction (only `whenNotPaused`). It calls `_getTotalEthInProtocol()`, which iterates over every supported asset and for each asset calls `LRTDepositPool.getTotalAssetDeposits(asset)`.

`getTotalAssetDeposits` calls `getAssetDistributionData`, which loops over every NDC in `nodeDelegatorQueue` and for each NDC calls `INodeDelegator(ndc).getAssetUnstaking(asset)`.

`getAssetUnstaking` in `NodeDelegator` calls `delegationManager.getQueuedWithdrawals(address(this))` — an external call to EigenLayer — and then iterates over every queued withdrawal and every strategy within each withdrawal.

The total gas cost scales as:

```
O(supportedAssets × NDCs × queuedWithdrawals_per_NDC × strategies_per_withdrawal)
```

With `maxNodeDelegatorLimit = 10`, `maxUncompletedWithdrawalCount` capped at 80, and multiple supported assets, the protocol's own comment in `LRTUnstakingVault.sol` acknowledges this risk:

> "120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price"

However, the cap of 80 applies only to protocol-initiated withdrawals. Forced undelegations by the EigenLayer operator can add additional queued withdrawals beyond this cap (the comment notes "Need buffer for theoretical operator forced undelegations (ndc count × asset count = 15)"). Furthermore, `getAssetUnstaking` is called `supportedAssets.length × NDCs.length` times, meaning `getQueuedWithdrawals` is invoked as many as 50 times (5 assets × 10 NDCs) per single `updateRSETHPrice()` call, each being a separate external call.

### Impact Explanation
If `updateRSETHPrice()` becomes uncallable due to OOG, the stored `rsETHPrice` in `LRTOracle` becomes permanently stale. This price is consumed by:
- `LRTDepositPool.getRsETHAmountToMint()` — used in every deposit to compute rsETH minted
- `LRTWithdrawalManager.unlockQueue()` — uses `lrtOracle.rsETHPrice()` to compute payout amounts for withdrawal requests

A stale price causes incorrect rsETH minting ratios for depositors and incorrect asset payouts for withdrawers, constituting a protocol-wide accounting failure. This maps to **Medium — Unbounded gas consumption** (and potentially temporary freezing of the price-update mechanism).

### Likelihood Explanation
The protocol already acknowledges the gas sensitivity of this path in its own comments. As the protocol grows (more assets added via `addNewSupportedAsset`, more NDCs added up to `maxNodeDelegatorLimit`, more EigenLayer queued withdrawals from normal operations or forced undelegations), the gas cost grows multiplicatively. This is a realistic operational scenario, not a theoretical edge case.

### Recommendation
1. Cache the result of `getQueuedWithdrawals` per NDC and reuse it across all asset iterations, rather than calling it once per (asset, NDC) pair.
2. Alternatively, maintain a per-NDC, per-asset accounting of unstaking amounts that is updated incrementally (on `initiateUnstaking` / `completeUnstaking`) rather than recomputed on every price update.
3. Consider adding a hard cap on the number of supported assets and NDCs such that the worst-case gas is provably within block limits.

### Proof of Concept

Call chain demonstrating the nested unbounded iteration:

```
updateRSETHPrice()                          // LRTOracle.sol:87 — public, no auth
  └─ _getTotalEthInProtocol()               // LRTOracle.sol:331 — loops over supportedAssets
       └─ getTotalAssetDeposits(asset)       // LRTDepositPool.sol:385 — per asset
            └─ getAssetDistributionData()    // LRTDepositPool.sol:426 — loops over nodeDelegatorQueue
                 └─ getAssetUnstaking(asset) // NodeDelegator.sol:405 — per (asset, NDC)
                      └─ getQueuedWithdrawals()  // external call to EigenLayer DelegationManager
                           └─ for each withdrawal → for each strategy  // NodeDelegator.sol:409-426
```

With 5 supported assets, 10 NDCs, and 80 queued withdrawals per NDC (each with 2 strategies):
- `getQueuedWithdrawals` is called **50 times** (5 × 10)
- Inner loop iterations: **5 × 10 × 80 × 2 = 8,000**

Each `getQueuedWithdrawals` call loads the full withdrawal queue from EigenLayer storage. At this scale, the transaction will exceed the block gas limit and revert, permanently preventing price updates. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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
