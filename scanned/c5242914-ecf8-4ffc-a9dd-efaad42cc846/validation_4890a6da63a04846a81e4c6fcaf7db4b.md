### Title
Unbounded Gas Consumption in `updateRSETHPrice()` via Nested Loops Over Assets × NDCs × Queued Withdrawals × Strategies — (File: `contracts/LRTOracle.sol`, `contracts/NodeDelegator.sol`, `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a `public` function callable by any address. Its internal call chain traverses a deeply nested set of loops: all supported assets → all node delegators → all queued EigenLayer withdrawals per NDC → all strategies per withdrawal. As the protocol scales, the gas cost of this function grows polynomially and can approach or exceed the block gas limit, permanently preventing price updates and disabling the protocol's auto-pause safety mechanism.

---

### Finding Description

The call chain triggered by `updateRSETHPrice()` is:

```
updateRSETHPrice()                          [public, no access control]
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for each asset (N):
                 getTotalAssetDeposits(asset)
                   └─ getAssetDistributionData(asset)
                        └─ for each NDC (M):
                             getAssetUnstaking(asset)   [NodeDelegator.sol]
                               └─ getQueuedWithdrawals(NDC)  [EigenLayer external call]
                                    └─ for each withdrawal (K):
                                         for each strategy (L):
                                              sharesToUnderlyingView(...)
```

Total iterations: **N × M × K × L**, each involving external calls.

`getAssetUnstaking` in `NodeDelegator.sol` calls `getQueuedWithdrawals` on EigenLayer's `DelegationManager` and then iterates over every queued withdrawal and every strategy within it — once per asset per NDC. Because the outer loop in `_getTotalEthInProtocol` is per-asset and the inner loop in `getAssetDistributionData` is per-NDC, the same set of queued withdrawals for a given NDC is re-traversed once for every supported asset.

The existing mitigations are incomplete:
- `maxNodeDelegatorLimit` defaults to 10 but is admin-adjustable upward with no hard ceiling.
- `maxUncompletedWithdrawalCount` is capped at 80 total, but this is a global count. The per-NDC withdrawal count is `80 / M`, and `getAssetUnstaking` iterates over all of them **N times** (once per asset). The developers' own comment acknowledges this: *"120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price"* — but the analysis counts total withdrawals, not the N × M × K × L product.
- The number of supported assets has no hard cap.

With a realistic configuration of 5 assets, 10 NDCs, 8 withdrawals per NDC (80 total), and 2 strategies per withdrawal:
- `getAssetUnstaking` is called **50 times** (5 × 10)
- Each call iterates over 8 withdrawals × 2 strategies = 16 inner iterations + 1 external `getQueuedWithdrawals` call
- Total: 50 × (1 external call + 16 strategy iterations) ≈ **5–10M gas** for this segment alone

If `maxNodeDelegatorLimit` is raised or more assets are added, the gas grows further.

---

### Impact Explanation

If `updateRSETHPrice()` exceeds the block gas limit:

1. The stored `rsETHPrice` becomes permanently stale. All deposits (`depositETH`, `depositAsset`) and withdrawals (`initiateWithdrawal`) continue using the stale price, causing incorrect rsETH minting and asset redemption amounts — a form of share/asset mis-accounting.
2. The auto-pause safety mechanism in `_updateRsETHPrice()` (which pauses `LRTDepositPool` and `LRTWithdrawalManager` on excessive price drops) can never trigger, removing the protocol's primary downside protection.
3. `updateRSETHPriceAsManager()` is subject to the same gas cost and would also fail.

**Impact: Medium — Unbounded gas consumption leading to temporary or permanent freezing of the price update mechanism and disabling of the auto-pause safety circuit.**

---

### Likelihood Explanation

The gas cost grows automatically as the protocol adds assets, node delegators, and processes EigenLayer withdrawals — all of which are normal operational activities. No attacker action is required to trigger the condition; it emerges from legitimate protocol scaling. The developers' own comment in `LRTUnstakingVault.sol` confirms awareness of the gas sensitivity of `updateRSETHPrice()`, but the bound they computed (total withdrawal count) understates the true cost (N_assets × N_NDCs × withdrawals_per_NDC × strategies_per_withdrawal).

**Likelihood: Medium.**

---

### Recommendation

1. Cache the result of `getQueuedWithdrawals` per NDC and reuse it across all asset iterations, rather than calling it once per asset per NDC.
2. Introduce a dedicated `totalAssetUnstaking` mapping in `LRTUnstakingVault` that is updated incrementally on `initiateUnstaking` / `completeUnstaking`, eliminating the need to iterate over EigenLayer queued withdrawals at price-update time.
3. Enforce a hard cap on the number of supported assets, or restructure `_getTotalEthInProtocol` to avoid the N × M × K × L traversal.
4. Add a gas-limit guard or circuit breaker that falls back to the last known price if the computation cannot complete.

---

### Proof of Concept

**Root cause — `updateRSETHPrice()` is public with no access control:** [1](#0-0) 

**`_getTotalEthInProtocol()` loops over all supported assets, calling `getTotalAssetDeposits` for each:** [2](#0-1) 

**`getAssetDistributionData` loops over all NDCs and calls `getAssetUnstaking` per NDC per asset:** [3](#0-2) 

**`getAssetUnstaking` in `NodeDelegator` calls `getQueuedWithdrawals` (external) and then iterates over all withdrawals × strategies — this is called N_assets × N_NDCs times per price update:** [4](#0-3) 

**The developers' own comment acknowledges the gas sensitivity but uses an incomplete bound (total count, not the N×M×K×L product):** [5](#0-4)

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
