### Title
Nested Iteration Over `nodeDelegatorQueue` × `supportedAssets` × Queued EigenLayer Withdrawals Causes Unbounded Gas Growth in Core User Functions - (File: contracts/NodeDelegator.sol, contracts/LRTDepositPool.sol, contracts/LRTOracle.sol)

---

### Summary

`NodeDelegator.getAssetUnstaking()` fetches and iterates over all queued EigenLayer withdrawals for a given NDC. This function is called inside a loop over `nodeDelegatorQueue` in `LRTDepositPool.getAssetDistributionData()` / `getETHDistributionData()`. That loop is itself called once per supported asset inside `LRTOracle._getTotalEthInProtocol()`. The resulting O(supportedAssets × NDCs × queuedWithdrawals × strategies) computation is embedded in every user-facing deposit, withdrawal initiation, and price-update call. As the protocol scales normally, these core functions grow increasingly expensive and can eventually revert with out-of-gas errors, temporarily freezing deposits, withdrawals, and rsETH price updates.

---

### Finding Description

**Root cause — `NodeDelegator.getAssetUnstaking()`**

`getAssetUnstaking()` calls EigenLayer's `getQueuedWithdrawals()` and then iterates over every queued withdrawal and every strategy within each withdrawal:

```solidity
// NodeDelegator.sol lines 405-427
function getAssetUnstaking(address asset) external view returns (uint256 amount) {
    (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
        _getDelegationManager().getQueuedWithdrawals(address(this));

    for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
        IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];
        for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
            ...
        }
    }
}
``` [1](#0-0) 

**First outer loop — `getAssetDistributionData()` / `getETHDistributionData()` iterate over all NDCs**

For every NDC in `nodeDelegatorQueue`, both functions call `getAssetUnstaking()`:

```solidity
// LRTDepositPool.sol lines 446-456
uint256 ndcsCount = nodeDelegatorQueue.length;
for (uint256 i; i < ndcsCount;) {
    assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);
    assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
    assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
    ...
}
``` [2](#0-1) 

The same pattern exists for ETH: [3](#0-2) 

**Second outer loop — `_getTotalEthInProtocol()` iterates over all supported assets**

`LRTOracle._getTotalEthInProtocol()` calls `getTotalAssetDeposits()` (which calls `getAssetDistributionData()`) for every supported asset:

```solidity
// LRTOracle.sol lines 336-348
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    ...
}
``` [4](#0-3) 

**Affected user-facing entry points**

| Function | Call chain to `getAssetUnstaking()` |
|---|---|
| `depositETH()` / `depositAsset()` | `_beforeDeposit()` → `getTotalAssetDeposits()` → `getAssetDistributionData()` → NDC loop → `getAssetUnstaking()` |
| `initiateWithdrawal()` | `getAvailableAssetAmount()` → `getTotalAssetDeposits()` → same chain |
| `updateRSETHPrice()` (public) | `_getTotalEthInProtocol()` → asset loop → `getTotalAssetDeposits()` → NDC loop → `getAssetUnstaking()` | [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

The total number of external calls to EigenLayer's `getQueuedWithdrawals()` in a single `updateRSETHPrice()` invocation is `supportedAssets.length × nodeDelegatorQueue.length`. Each such call returns up to `maxUncompletedWithdrawalCount` (capped at 80) withdrawal structs, each of which is then iterated over with a nested strategy loop. [9](#0-8) 

---

### Impact Explanation

**Medium — Unbounded gas consumption / Temporary freezing of funds.**

As the protocol scales through normal operation (more NDCs added, more assets supported, more EigenLayer unstaking operations queued), the gas cost of `depositETH()`, `depositAsset()`, `initiateWithdrawal()`, and `updateRSETHPrice()` grows as O(supportedAssets × NDCs × queuedWithdrawals × strategies). At sufficient scale, these transactions will revert with out-of-gas errors, temporarily preventing deposits, withdrawals, and rsETH price updates. A stale or un-updatable rsETH price further blocks minting.

---

### Likelihood Explanation

**Medium.** The protocol is designed to scale: `maxNodeDelegatorLimit` starts at 10 but is admin-adjustable upward, the supported asset list grows over time, and EigenLayer unstaking operations accumulate during normal restaking lifecycle. No attacker action is required — ordinary protocol growth triggers the condition. The `updateRSETHPrice()` function is public and callable by anyone, meaning any user's deposit or withdrawal attempt will pay the full accumulated gas cost. [10](#0-9) [11](#0-10) 

---

### Recommendation

1. **Cache `getAssetUnstaking()` results**: Compute the total unstaking amount for all assets in a single pass over `getQueuedWithdrawals()` per NDC, rather than calling it once per asset per NDC.
2. **Decouple TVL accounting from real-time EigenLayer queries**: Store a cached/snapshotted `assetUnstaking` value that is updated lazily (e.g., when `completeUnstaking()` is called) rather than fetching live from EigenLayer on every deposit/withdrawal.
3. **Separate the `_getTotalEthInProtocol()` loop from per-asset `getAssetDistributionData()` calls**: Compute NDC balances once across all assets in a single NDC loop, rather than re-iterating the NDC queue once per supported asset.

---

### Proof of Concept

With `N` supported assets, `M` NDCs, and `W` queued withdrawals per NDC (up to 80 total), a single call to `updateRSETHPrice()` or `depositETH()` triggers:

- `N × M` calls to `getQueuedWithdrawals()` (external EigenLayer calls)
- `N × M × W` iterations of the outer withdrawal loop in `getAssetUnstaking()`
- `N × M × W × S` iterations of the inner strategy loop (where `S` = strategies per withdrawal)

With realistic values (5 assets, 10 NDCs, 80 total withdrawals, 3 strategies each): **5 × 10 × 80 × 3 = 12,000 loop iterations** plus **50 external calls** per `updateRSETHPrice()` invocation. If `maxNodeDelegatorLimit` is raised (e.g., to 50) and more assets are added, the gas cost grows proportionally, eventually causing out-of-gas reverts on all deposit and withdrawal paths. [1](#0-0) [12](#0-11) [13](#0-12)

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

**File:** contracts/LRTDepositPool.sol (L29-33)
```text
    uint256 public maxNodeDelegatorLimit;
    uint256 public minAmountToDeposit;

    mapping(address => uint256) public isNodeDelegator; // 0: not a node delegator, 1: is a node delegator
    address[] public nodeDelegatorQueue;
```

**File:** contracts/LRTDepositPool.sol (L86-93)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
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

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
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
