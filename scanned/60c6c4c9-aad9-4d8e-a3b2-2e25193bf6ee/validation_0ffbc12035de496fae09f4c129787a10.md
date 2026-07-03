### Title
Unbounded Nested Loop in `updateRSETHPrice()` via `_getTotalEthInProtocol()` Can Permanently Freeze Price Updates and User Deposits/Withdrawals - (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public function that internally executes a three-level nested loop whose total iteration count scales as `|supportedAssets| × |nodeDelegatorQueue| × |queuedWithdrawalsPerNDC|`. As the protocol grows normally — more supported assets, more NodeDelegators, more EigenLayer withdrawal queues — this function will eventually exceed the Ethereum block gas limit and become permanently uncallable. Because the same `getTotalAssetDeposits()` helper is invoked on every user deposit and withdrawal initiation, the same gas exhaustion also permanently freezes `depositETH()`, `depositAsset()`, and `initiateWithdrawal()`.

---

### Finding Description

The call chain is:

```
updateRSETHPrice()                          [public, no access control]
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for each asset in supportedAssetList:          // LOOP 1 — no cap
                 getTotalAssetDeposits(asset)
                   └─ getAssetDistributionData(asset)
                        └─ for each NDC in nodeDelegatorQueue: // LOOP 2 — capped by maxNodeDelegatorLimit
                             getAssetUnstaking(asset)
                               └─ getQueuedWithdrawals(NDC)   // external EigenLayer call
                                    └─ for each withdrawal:   // LOOP 3 — capped by maxUncompletedWithdrawalCount
                                         for each strategy:
                                              sharesToUnderlyingView(...)
```

`supportedAssetList` in `LRTConfig` has **no explicit cap** — assets are added via `addNewSupportedAsset()` as the protocol expands. [1](#0-0) 

`nodeDelegatorQueue` is bounded by `maxNodeDelegatorLimit` (default 10, admin-settable). [2](#0-1) 

`maxUncompletedWithdrawalCount` is an admin-settable parameter in `LRTUnstakingVault`. [3](#0-2) 

`_getTotalEthInProtocol()` iterates over every supported asset and calls `getTotalAssetDeposits()` for each: [4](#0-3) 

`getAssetDistributionData()` then loops over every NDC and calls `getAssetUnstaking()` for each: [5](#0-4) 

`getAssetUnstaking()` fetches **all** queued EigenLayer withdrawals and iterates over them with a nested strategy loop: [6](#0-5) 

The same `getTotalAssetDeposits()` is also called from every user deposit and withdrawal initiation path:

- `depositETH()` / `depositAsset()` → `_beforeDeposit()` → `_checkIfDepositAmountExceedesCurrentLimit()` → `getTotalAssetDeposits()` [7](#0-6) 
- `initiateWithdrawal()` → `getAvailableAssetAmount()` → `getTotalAssetDeposits()` [8](#0-7) 

---

### Impact Explanation

**Severity: Medium — Unbounded gas consumption / Temporary (potentially permanent) freezing of funds.**

Once the product of `|supportedAssets| × |nodeDelegatorQueue| × |maxUncompletedWithdrawalCount|` grows large enough to exceed the ~30M block gas limit, the following functions become permanently uncallable in a single transaction:

1. `updateRSETHPrice()` — the rsETH price oracle stalls; the stale price is used for all subsequent mints and withdrawals, causing share/asset mis-accounting.
2. `depositETH()` / `depositAsset()` — users cannot deposit.
3. `initiateWithdrawal()` — users cannot queue withdrawals.

With 10 supported assets, 10 NDCs, and `maxUncompletedWithdrawalCount` = 50, the inner loop executes up to 5,000 iterations, each involving external calls to EigenLayer's `sharesToUnderlyingView()`. This is already a realistic configuration for a mature deployment. [9](#0-8) 

---

### Likelihood Explanation

**Probability: Medium.**

This is not a one-time attack — it is a natural consequence of protocol growth. Every new supported asset multiplies the gas cost of every deposit, withdrawal, and price update. The protocol is designed to support multiple LSTs and multiple NodeDelegators simultaneously, and `maxUncompletedWithdrawalCount` is expected to be non-trivial to support real unstaking operations. No attacker action is required; the protocol simply grows into the failure condition. [10](#0-9) 

---

### Recommendation

1. **Batch `_getTotalEthInProtocol()`**: Instead of computing the full TVL in one call, cache per-asset TVL snapshots that are updated lazily or in bounded batches, analogous to the BtcPoller fix of committing every N blocks.
2. **Cache `getAssetUnstaking()` results**: Store the unstaking amount per NDC per asset in storage and update it only when withdrawals are queued or completed, rather than recomputing it on every price update and deposit.
3. **Decouple deposit/withdrawal limit checks from full TVL computation**: `_checkIfDepositAmountExceedesCurrentLimit()` should not trigger a full cross-NDC EigenLayer scan on every user deposit.
4. **Cap `supportedAssetList`**: Introduce an explicit maximum number of supported assets, similar to `maxNodeDelegatorLimit`.

---

### Proof of Concept

Assume the protocol has reached:
- 8 supported assets (`supportedAssetList.length = 8`)
- 10 NDCs (`nodeDelegatorQueue.length = 10`, at `maxNodeDelegatorLimit`)
- 40 uncompleted withdrawals per NDC (`maxUncompletedWithdrawalCount = 40`)

A call to `updateRSETHPrice()` triggers:
- 8 × 10 = 80 calls to `getAssetUnstaking()`
- Each `getAssetUnstaking()` call fetches 40 queued withdrawals from EigenLayer and iterates over their strategies
- Each iteration calls `strategy.sharesToUnderlyingView()` — an external SLOAD-heavy call

Total: ~3,200 external calls in a single transaction. At ~5,000 gas per external call (cold), this alone is ~16M gas, before accounting for the surrounding logic. Adding the `getAssetBalance()` calls (also EigenLayer external calls) at the same scale pushes the total well past the 30M block gas limit, making `updateRSETHPrice()`, `depositETH()`, and `initiateWithdrawal()` all permanently uncallable. [11](#0-10) [6](#0-5)

### Citations

**File:** contracts/LRTConfig.sol (L26-26)
```text
    address[] public supportedAssetList;
```

**File:** contracts/LRTConfig.sol (L99-100)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
```

**File:** contracts/LRTDepositPool.sol (L29-29)
```text
    uint256 public maxNodeDelegatorLimit;
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

**File:** contracts/LRTUnstakingVault.sol (L39-40)
```text
    uint256 public uncompletedWithdrawalCount;
    uint256 public maxUncompletedWithdrawalCount;
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

**File:** contracts/NodeDelegator.sol (L406-427)
```text
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
