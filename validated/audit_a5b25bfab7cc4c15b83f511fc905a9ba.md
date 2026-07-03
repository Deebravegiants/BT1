### Title
Multiplicatively Unbounded Gas in `updateRSETHPrice()` Due to Nested Cross-Contract Loops — (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is publicly callable and triggers a deeply nested call chain that makes O(assets × NDCs) external calls to EigenLayer's `getQueuedWithdrawals()`, plus O(assets × NDCs × withdrawals × strategies) calls to `strategy.sharesToUnderlyingView()`. As the protocol scales normally — more supported assets, more NodeDelegators, more queued withdrawals — the gas cost grows multiplicatively, eventually making the function uncallable and freezing the protocol's price update mechanism.

---

### Finding Description

The call chain starting from the public `updateRSETHPrice()` function is:

```
updateRSETHPrice()                          [LRTOracle.sol:87]
  └─ _updateRsETHPrice()                    [LRTOracle.sol:214]
       └─ _getTotalEthInProtocol()          [LRTOracle.sol:331]
            └─ for each supported asset (N):
                 └─ getTotalAssetDeposits() [LRTDepositPool.sol:385]
                      └─ getAssetDistributionData() [LRTDepositPool.sol:426]
                           └─ for each NDC (M):
                                └─ getAssetUnstaking(asset) [NodeDelegator.sol:405]
                                     └─ getQueuedWithdrawals() [external EigenLayer call]
                                          └─ for each withdrawal (W):
                                               └─ for each strategy (S):
                                                    └─ sharesToUnderlyingView() [external call]
```

**Step 1 — `_getTotalEthInProtocol()` loops over all supported assets:** [1](#0-0) 

**Step 2 — `getAssetDistributionData()` loops over all NDCs and calls `getAssetUnstaking()` per NDC per asset:** [2](#0-1) 

**Step 3 — `getAssetUnstaking()` makes an external call to EigenLayer's `getQueuedWithdrawals()` and then iterates over every queued withdrawal and every strategy within it:** [3](#0-2) 

The critical redundancy is that `getQueuedWithdrawals(address(this))` is called once per (asset, NDC) pair. For a given NDC, the queued withdrawals are identical regardless of which asset is being queried, yet the external call is repeated N times (once per supported asset). This is the direct analog of the Holdefi excessive-indirection pattern: the same external data is fetched repeatedly due to the factored structure of the call chain.

The total number of external calls is:
- `getQueuedWithdrawals()`: **N × M** calls
- `sharesToUnderlyingView()`: **N × M × W × S** calls

where N = supported assets, M = NDCs, W = queued withdrawals per NDC, S = strategies per withdrawal.

---

### Impact Explanation

`updateRSETHPrice()` is a critical function — it updates the rsETH/ETH exchange rate used by `LRTDepositPool` for all deposits and rsETH minting. If the gas cost of this function exceeds the block gas limit, it becomes permanently uncallable. This would freeze the protocol's price update mechanism, preventing new deposits from being correctly priced and effectively halting the protocol.

**Impact: Medium — Unbounded gas consumption / Temporary freezing of funds.**

---

### Likelihood Explanation

The gas cost grows with normal protocol operation:
- The number of supported assets is admin-controlled and grows as new LSTs are added.
- `maxNodeDelegatorLimit` defaults to 10 but is admin-increasable via `updateMaxNodeDelegatorLimit()`. [4](#0-3) 

- The number of queued withdrawals per NDC grows as operators call `initiateUnstaking()` and `undelegate()`. The global `maxUncompletedWithdrawalCount` in `LRTUnstakingVault` bounds the total across all NDCs, but this value is admin-settable and could be large. [5](#0-4) 

With 5 supported assets, 10 NDCs, and 20 queued withdrawals per NDC (each with 2 strategies), the function already makes 50 `getQueuedWithdrawals()` external calls and 200 `sharesToUnderlyingView()` external calls per invocation. At realistic EigenLayer gas costs per external call, this approaches block gas limits at moderate scale.

---

### Recommendation

1. **Decouple asset iteration from NDC withdrawal fetching.** In `getAssetDistributionData()`, fetch `getQueuedWithdrawals()` once per NDC (not once per asset per NDC) and compute the unstaking amount for all assets in a single pass over the returned withdrawals.
2. **Cache `getQueuedWithdrawals()` results** within a single `updateRSETHPrice()` call, or restructure `getAssetUnstaking()` to accept pre-fetched withdrawal data.
3. **Add a gas guard** or cap on the number of supported assets × NDCs to ensure `updateRSETHPrice()` remains callable within block gas limits.

---

### Proof of Concept

Call `updateRSETHPrice()` on a mainnet fork with:
- 5 supported assets (stETH, rETH, cbETH, swETH, ETH)
- 10 NDCs each with 10 queued withdrawals (2 strategies each)

Observe that `getQueuedWithdrawals()` is called 50 times (5 assets × 10 NDCs) and `sharesToUnderlyingView()` is called 100 times (5 × 10 × 2), with each being a cross-contract call. Measure gas consumption and compare against the block gas limit. As `maxUncompletedWithdrawalCount` is increased and more NDCs are added, the function will eventually revert with out-of-gas.

The entry path is fully permissionless: `updateRSETHPrice()` has no access control. [6](#0-5)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

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

**File:** contracts/LRTUnstakingVault.sol (L39-40)
```text
    uint256 public uncompletedWithdrawalCount;
    uint256 public maxUncompletedWithdrawalCount;
```
