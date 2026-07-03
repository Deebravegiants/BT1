### Title
Unbounded Nested Gas Consumption in `updateRSETHPrice()` via Redundant `getQueuedWithdrawals()` Calls Across All Assets Per NDC — (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public, permissionless function. Its internal call chain produces a multi-level nested loop: for every supported asset it calls `getTotalAssetDeposits()`, which loops over every NDC and calls `NodeDelegator.getAssetUnstaking()` on each. `getAssetUnstaking()` issues a fresh external call to `DelegationManager.getQueuedWithdrawals()` and then runs a nested loop over every queued withdrawal and every strategy within it. The same EigenLayer storage is read `(assets × NDCs)` times per price update. As the protocol scales — more supported assets, more NDCs, more queued withdrawals — gas consumption grows multiplicatively with no hardcoded ceiling, and can exceed the Ethereum block gas limit, permanently bricking price updates and all user-facing deposit/withdrawal entry points that depend on `getTotalAssetDeposits()`.

---

### Finding Description

**Call chain for `updateRSETHPrice()`:**

```
updateRSETHPrice()                          [public, no access control]
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for each supportedAsset:          ← loop A (assets)
                 getTotalAssetDeposits(asset)
                   └─ getAssetDistributionData(asset)
                        └─ for each NDC:          ← loop B (NDCs)
                             getAssetUnstaking(asset)
                               └─ getQueuedWithdrawals(NDC)  ← expensive external call
                               └─ for each withdrawal:        ← loop C
                                    for each strategy:        ← loop D
                                         sharesToUnderlyingView()
```

`_getTotalEthInProtocol()` iterates over every supported asset: [1](#0-0) 

For each asset, `getAssetDistributionData()` iterates over every NDC and calls `getAssetUnstaking()`: [2](#0-1) 

`getAssetUnstaking()` issues a fresh `getQueuedWithdrawals()` external call and then runs a nested loop over all queued withdrawals and all strategies within each withdrawal: [3](#0-2) 

**The redundancy:** `getQueuedWithdrawals(NDC_i)` is called once per supported asset per NDC. With `A` supported assets and `M` NDCs, the same EigenLayer storage slot is read `A × M` times per `updateRSETHPrice()` invocation. Each call then re-executes the nested withdrawal × strategy loop. This is directly analogous to the Megapot bug where `generateSubsets()` was called `bonusballMax × normalTiers` times instead of being cached once.

**Controlling parameters — none have a hardcoded ceiling:**

- `maxNodeDelegatorLimit` — set by admin, initially 10, can be raised arbitrarily: [4](#0-3) 

- `maxUncompletedWithdrawalCount` — set by admin in `LRTUnstakingVault`, no upper bound enforced in `NodeDelegator`: [5](#0-4) 

- Number of supported assets — added by admin via `LRTConfig`, no hardcoded limit.

**Secondary entry paths that also trigger the expensive computation:**

`depositAsset()` / `depositETH()` → `_beforeDeposit()` → `_checkIfDepositAmountExceedesCurrentLimit()` → `getTotalAssetDeposits()` → `getAssetDistributionData()` → `getAssetUnstaking()` (for a single asset, but still O(NDCs × withdrawals × strategies)): [6](#0-5) 

`initiateWithdrawal()` → `getAvailableAssetAmount()` → `getTotalAssetDeposits()` → same chain: [7](#0-6) 

---

### Impact Explanation

If the cumulative gas for `updateRSETHPrice()` exceeds the Ethereum block gas limit (~30M gas), the function becomes permanently uncallable. The rsETH price stored in `rsETHPrice` will never be updated, causing:

1. **Permanent freeze of price updates** — `rsETHPrice` becomes stale; all downstream consumers (withdrawal amount calculations, deposit mint calculations) use a wrong rate.
2. **Permanent freeze of deposits** — `depositAsset()` / `depositETH()` call `getTotalAssetDeposits()` and will also OOG, making deposits impossible.
3. **Permanent freeze of withdrawal initiation** — `initiateWithdrawal()` calls `getAvailableAssetAmount()` → `getTotalAssetDeposits()` and will also OOG.

This matches the **Medium — Unbounded gas consumption** and **Critical — Permanent freezing of funds** impact categories.

---

### Likelihood Explanation

`updateRSETHPrice()` carries no access control — any address can call it: [8](#0-7) 

As the protocol grows organically (more LSTs supported, more NDCs added to increase throughput, more EigenLayer withdrawal batches queued), the gas cost rises multiplicatively. An admin increasing `maxNodeDelegatorLimit` from 10 to 20 while supporting 6 assets and having 30 queued withdrawals per NDC would produce `6 × 20 × 30 = 3600` inner loop iterations plus `6 × 20 = 120` external `getQueuedWithdrawals()` calls per `updateRSETHPrice()` invocation — each external call itself reading a dynamic-length array from EigenLayer storage. This is a realistic operational configuration.

---

### Recommendation

1. **Cache `getQueuedWithdrawals()` per NDC** and reuse the result across all asset iterations, eliminating the `A × M` redundant external calls. Restructure `_getTotalEthInProtocol()` to fetch all queued withdrawals once per NDC and compute per-asset unstaking amounts in a single pass.

2. **Introduce a hardcoded ceiling** on `maxNodeDelegatorLimit` and `maxUncompletedWithdrawalCount` (analogous to the Megapot recommendation to hardcode a limit on `bonusballMax`).

3. **Decouple `getAssetUnstaking()` from the price-update hot path** by maintaining a cached, incrementally updated unstaking balance that is updated only when withdrawals are queued or completed, rather than recomputed from scratch on every price update.

---

### Proof of Concept

With:
- 6 supported assets
- 15 NDCs (`maxNodeDelegatorLimit` raised to 15)
- 20 queued withdrawals per NDC (each with 2 strategies)

`updateRSETHPrice()` triggers:
- `6 × 15 = 90` external calls to `getQueuedWithdrawals()` (each reading a 20-element array from EigenLayer storage)
- `6 × 15 × 20 × 2 = 3600` inner loop iterations, each calling `strategy.sharesToUnderlyingView()` (another external call)

Total external calls per `updateRSETHPrice()`: `90 + 3600 = 3690`. At ~2100 gas per cold SLOAD and ~700 gas per warm SLOAD, plus call overhead, this easily exceeds 30M gas. Once this threshold is crossed, `updateRSETHPrice()` is permanently uncallable, and since `depositAsset()` also calls `getTotalAssetDeposits()`, user deposits are simultaneously bricked.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L336-348)
```text
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

**File:** contracts/LRTDepositPool.sol (L290-296)
```text
    function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
        if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
            revert InvalidMaximumNodeDelegatorLimit();
        }

        maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
        emit MaxNodeDelegatorLimitUpdated(maxNodeDelegatorLimit);
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

**File:** contracts/NodeDelegator.sol (L304-305)
```text
        if (_getUnstakingVault().uncompletedWithdrawalCount() >= _getUnstakingVault().maxUncompletedWithdrawalCount()) {
            revert MaxUncompletedWithdrawalsReached();
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

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```
