### Title
Unbounded Nested-Loop Gas Consumption in `getAssetUnstaking` Propagates Through Every Deposit and Withdrawal Path — (File: `contracts/NodeDelegator.sol`, `contracts/LRTDepositPool.sol`, `contracts/LRTOracle.sol`)

---

### Summary

`NodeDelegator.getAssetUnstaking()` fetches the full list of pending EigenLayer withdrawals via `getQueuedWithdrawals()` and iterates over them with a nested loop. This function is called once per NDC per asset inside `LRTDepositPool.getAssetDistributionData()` and `getETHDistributionData()`, which are themselves called on every user deposit (`depositETH`, `depositAsset`), every withdrawal initiation (`initiateWithdrawal`), and the public `LRTOracle.updateRSETHPrice()`. As the protocol scales — more supported assets, more NDCs, more queued EigenLayer withdrawals — the cumulative gas cost of these nested loops grows without a hard ceiling and can exceed the block gas limit, permanently bricking deposits and withdrawal initiations.

---

### Finding Description

**Root cause — `NodeDelegator.getAssetUnstaking()`:**

```solidity
// contracts/NodeDelegator.sol  lines 405-427
function getAssetUnstaking(address asset) external view returns (uint256 amount) {
    (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
        _getDelegationManager().getQueuedWithdrawals(address(this));   // ← full list, no pagination

    for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
        IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];
        for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
            ...
        }
    }
}
``` [1](#0-0) 

**Propagation into `getAssetDistributionData()` — called on every deposit:**

```solidity
// contracts/LRTDepositPool.sol  lines 446-456
uint256 ndcsCount = nodeDelegatorQueue.length;
for (uint256 i; i < ndcsCount;) {
    assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);
    assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
    assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset); // ← nested loop per NDC
    ...
}
``` [2](#0-1) 

`getETHDistributionData()` has the identical pattern: [3](#0-2) 

**Propagation into `_getTotalEthInProtocol()` — called by the public `updateRSETHPrice()`:**

```solidity
// contracts/LRTOracle.sol  lines 336-348
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {   // ← outer loop: all supported assets (no hard cap)
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    // ↑ calls getAssetDistributionData → loops over all NDCs → calls getAssetUnstaking per NDC
    ...
}
``` [4](#0-3) 

**`updateRSETHPrice()` is public with no access control:** [5](#0-4) 

**`supportedAssetList` has no hard cap:** [6](#0-5) 

**The total gas cost per call scales as:**

```
O(supportedAssets × ndcCount × queuedWithdrawals × strategiesPerWithdrawal)
```

- `supportedAssets`: no hard cap in `LRTConfig.supportedAssetList`
- `ndcCount`: up to `maxNodeDelegatorLimit` (admin-raiseable, default 10)
- `queuedWithdrawals`: up to `maxUncompletedWithdrawalCount` (max 80 per the setter)
- `strategiesPerWithdrawal`: variable, protocol-controlled

The comment in `LRTUnstakingVault.setMaxUncompletedWithdrawalCount()` itself acknowledges the gas concern:

```solidity
// 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
if (_maxUncompletedWithdrawalCount > 80) {
    revert MaxUncompletedWithdrawalCountTooHigh();
}
``` [7](#0-6) 

This cap only bounds one dimension. With 5 supported assets, 10 NDCs, and 80 queued withdrawals, `updateRSETHPrice()` already triggers **50 separate `getQueuedWithdrawals()` calls**, each deserializing up to 80 `Withdrawal` structs from EigenLayer storage. Adding more assets (a routine governance action) multiplies this cost further with no ceiling.

---

### Impact Explanation

When the cumulative gas cost exceeds the block gas limit:

1. **`depositETH()` / `depositAsset()`** revert with OOG — no new deposits can be made. This is a **temporary (potentially permanent) freezing of user funds in transit** and a denial of the protocol's core service.
2. **`initiateWithdrawal()`** reverts with OOG — rsETH holders cannot queue withdrawals, freezing their ability to exit.
3. **`updateRSETHPrice()`** reverts — the rsETH price becomes permanently stale, disabling fee accrual and the price-drop circuit-breaker that auto-pauses the protocol.

Impact classification: **Medium — Temporary (escalating to permanent) freezing of funds; unbounded gas consumption.**

---

### Likelihood Explanation

The protocol is designed to grow: more LST collateral types are added via governance, more NDCs are deployed to scale EigenLayer restaking, and queued withdrawals accumulate during normal operations. Each of these legitimate growth steps increases the gas cost of every deposit and withdrawal. No single attacker action is required — the DoS emerges from ordinary protocol scaling. The protocol's own comment acknowledges the gas ceiling concern, confirming the team is aware of the pressure but has only partially mitigated it (bounding one dimension while leaving others uncapped).

---

### Recommendation

1. **Cache `getQueuedWithdrawals()` results**: Do not call `getAssetUnstaking()` once per NDC per asset. Instead, fetch queued withdrawals once per NDC and compute all asset amounts in a single pass.
2. **Hard-cap `supportedAssetList`**: Add a `maxSupportedAssets` limit analogous to `maxNodeDelegatorLimit`.
3. **Decouple accounting from live EigenLayer queries**: Store a per-NDC per-asset `unstakingAmount` that is updated lazily (on `initiateUnstaking` / `completeUnstaking`) rather than recomputed on every read. This eliminates the live `getQueuedWithdrawals()` call from the deposit/withdrawal hot path entirely.
4. **Paginate `_getTotalEthInProtocol()`**: Allow partial updates across multiple transactions rather than computing the full TVL in one call.

---

### Proof of Concept

```
// Scenario: 5 supported assets, 10 NDCs, 80 queued withdrawals each, 2 strategies per withdrawal

// Step 1: Admin adds 5 LST assets to LRTConfig (routine governance)
// Step 2: Admin deploys 10 NodeDelegator contracts (routine scaling)
// Step 3: Operator queues 80 EigenLayer withdrawals across NDCs (routine unstaking)

// Step 4: Any user calls depositETH():
//   → _checkIfDepositAmountExceedesCurrentLimit()
//   → getTotalAssetDeposits(ETH)
//   → getETHDistributionData()
//   → for each of 10 NDCs: getAssetUnstaking(ETH)
//     → getQueuedWithdrawals() [10 calls, each returning 80 withdrawals × 2 strategies]
//   Total inner iterations: 10 × 80 × 2 = 1,600 storage reads from EigenLayer

// Step 5: updateRSETHPrice() (public, no auth):
//   → _getTotalEthInProtocol()
//   → for each of 5 assets: getTotalAssetDeposits()
//     → getAssetDistributionData() → 10 NDCs × getAssetUnstaking()
//   Total getQueuedWithdrawals() calls: 5 × 10 = 50
//   Total inner iterations: 50 × 80 × 2 = 8,000 EigenLayer storage reads

// As supportedAssets grows to 10 and maxNodeDelegatorLimit is raised to 20:
//   Total inner iterations: 10 × 20 × 80 × 2 = 32,000 → exceeds block gas limit
//   → depositETH(), initiateWithdrawal(), updateRSETHPrice() all revert with OOG
```

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

**File:** contracts/LRTConfig.sol (L106-118)
```text
    function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
        UtilLib.checkNonZeroAddress(asset);
        if (depositLimit == 0) {
            revert InvalidDepositLimit();
        }
        if (isSupportedAsset[asset]) {
            revert AssetAlreadySupported();
        }
        isSupportedAsset[asset] = true;
        supportedAssetList.push(asset);
        depositLimitByAsset[asset] = depositLimit;
        emit AddedNewSupportedAsset(asset, depositLimit);
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
