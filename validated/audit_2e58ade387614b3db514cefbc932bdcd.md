### Title
`maxUncompletedWithdrawalCount` Has No Effect — Limit Is Never Enforced in `increaseUncompletedWithdrawalCount` - (File: `contracts/LRTUnstakingVault.sol`)

---

### Summary

`LRTUnstakingVault` declares `maxUncompletedWithdrawalCount` and provides `setMaxUncompletedWithdrawalCount` to cap the number of in-flight EigenLayer withdrawals. The setter even enforces a hard ceiling of 80 with an explicit comment warning that exceeding ~120 uncompleted withdrawals will break `updateRSETHPrice()`. However, `increaseUncompletedWithdrawalCount()` — the only function that increments the counter — never checks the cap. The variable is therefore dead configuration: `uncompletedWithdrawalCount` can grow without bound, eventually causing `updateRSETHPrice()` to exhaust block gas and become permanently uncallable.

---

### Finding Description

In `LRTUnstakingVault.sol`, the state variable and its setter are:

```solidity
// Line 40
uint256 public maxUncompletedWithdrawalCount;

// Lines 150-159
function setMaxUncompletedWithdrawalCount(uint256 _maxUncompletedWithdrawalCount) external onlyLRTManager {
    // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
    // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
    if (_maxUncompletedWithdrawalCount > 80) {
        revert MaxUncompletedWithdrawalCountTooHigh();
    }
    maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;
    emit MaxUncompletedWithdrawalCountSet(_maxUncompletedWithdrawalCount);
}
```

The function that increments the counter is:

```solidity
// Lines 184-186
function increaseUncompletedWithdrawalCount() external onlyLRTNodeDelegator {
    uncompletedWithdrawalCount++;
}
```

There is no `require(uncompletedWithdrawalCount < maxUncompletedWithdrawalCount, ...)` guard anywhere. The cap is stored and emitted but never read during the increment path. Every time a `NodeDelegator` queues an EigenLayer withdrawal it calls `increaseUncompletedWithdrawalCount()`, and the counter grows past the intended ceiling silently.

The gas concern is concrete. `LRTOracle._updateRsETHPrice()` calls `_getTotalEthInProtocol()`, which iterates over every supported asset and calls `ILRTDepositPool.getTotalAssetDeposits(asset)`. That function calls `INodeDelegator.getAssetUnstaking(asset)` for every NodeDelegator in the queue. `getAssetUnstaking` queries EigenLayer's `DelegationManager.getQueuedWithdrawals`, whose on-chain iteration cost scales with the number of pending withdrawals. The protocol's own comment acknowledges the ceiling is ~120 total uncompleted withdrawals before the price update breaks.

---

### Impact Explanation

When `uncompletedWithdrawalCount` exceeds the safe threshold (acknowledged by the protocol as ~120), `updateRSETHPrice()` in `LRTOracle` will revert with an out-of-gas error on every call. `updateRSETHPrice()` is a public function that must succeed for the protocol to function: it is the only mechanism that refreshes `rsETHPrice`, which is used by both `LRTDepositPool.getRsETHAmountToMint()` (deposits) and `LRTWithdrawalManager.getExpectedAssetAmount()` (withdrawals). A stale or permanently frozen price update constitutes **unbounded gas consumption** leading to a **temporary freeze of funds** — users cannot deposit or withdraw at a correct rate, and the oracle-driven price protection mechanisms (pause-on-drop) also stop working.

**Impact: Medium — Unbounded gas consumption / temporary freezing of funds.**

---

### Likelihood Explanation

No attacker action is required. Normal protocol operation — operators queuing EigenLayer unstaking across multiple NodeDelegators and assets — accumulates uncompleted withdrawals. With up to 10 NodeDelegators (`maxNodeDelegatorLimit`) and multiple supported assets, the counter can reach the danger zone through routine restaking lifecycle activity. Because the cap is never enforced, there is no on-chain signal or revert to warn operators before the threshold is crossed.

---

### Recommendation

Enforce the cap inside `increaseUncompletedWithdrawalCount`:

```solidity
function increaseUncompletedWithdrawalCount() external onlyLRTNodeDelegator {
    if (maxUncompletedWithdrawalCount > 0 &&
        uncompletedWithdrawalCount >= maxUncompletedWithdrawalCount) {
        revert MaxUncompletedWithdrawalCountReached();
    }
    uncompletedWithdrawalCount++;
}
```

The `maxUncompletedWithdrawalCount > 0` guard preserves the ability to disable the cap (zero = unlimited) while ensuring the limit is actually applied when set.

---

### Proof of Concept

1. Manager calls `setMaxUncompletedWithdrawalCount(50)`. `maxUncompletedWithdrawalCount` is stored as `50`.
2. Operators initiate 51 EigenLayer unstaking operations across NodeDelegators. Each NodeDelegator calls `increaseUncompletedWithdrawalCount()`. No revert occurs; `uncompletedWithdrawalCount` reaches `51`.
3. Continue until `uncompletedWithdrawalCount` exceeds ~120.
4. Any caller invokes `LRTOracle.updateRSETHPrice()`. The call iterates `getQueuedWithdrawals` across all NDCs and all assets, consuming gas proportional to the total queued withdrawal count. The transaction reverts out-of-gas.
5. `rsETHPrice` is now permanently stale. Deposits and withdrawals use an incorrect exchange rate; the downside-protection auto-pause cannot trigger.

**Root cause lines:** [1](#0-0) [2](#0-1) [3](#0-2) 

**Gas-exhaustion sink:** [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTUnstakingVault.sol (L40-40)
```text
    uint256 public maxUncompletedWithdrawalCount;
```

**File:** contracts/LRTUnstakingVault.sol (L150-159)
```text
    function setMaxUncompletedWithdrawalCount(uint256 _maxUncompletedWithdrawalCount) external onlyLRTManager {
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;

        emit MaxUncompletedWithdrawalCountSet(_maxUncompletedWithdrawalCount);
    }
```

**File:** contracts/LRTUnstakingVault.sol (L184-186)
```text
    function increaseUncompletedWithdrawalCount() external onlyLRTNodeDelegator {
        uncompletedWithdrawalCount++;
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

**File:** contracts/LRTDepositPool.sol (L447-456)
```text
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }
```
