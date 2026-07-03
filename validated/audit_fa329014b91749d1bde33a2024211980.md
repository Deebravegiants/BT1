### Title
Protocol Fee Permanently Lost When `updateRSETHPrice()` Is Called While `LRTDepositPool` or `LRTWithdrawalManager` Is Paused - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` is only gated by `whenNotPaused`, which checks `LRTOracle.paused`. However, `_updateRsETHPrice()` internally computes a broader `protocolPaused` flag that also covers `lrtDepositPool.paused()` and `withdrawalManager.paused()`. When either of those two contracts is paused but `LRTOracle` itself is not, any unprivileged caller can invoke `updateRSETHPrice()`, which skips fee minting yet still advances `rsETHPrice` to the current TVL. This permanently moves the fee-accounting baseline forward, so the protocol fee for all yield accrued during the pause window is irrecoverably lost.

---

### Finding Description

`updateRSETHPrice()` passes its access check whenever `LRTOracle.paused == false`:

```solidity
// contracts/LRTOracle.sol:87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

Inside `_updateRsETHPrice()`, the broader pause state is evaluated:

```solidity
// contracts/LRTOracle.sol:236-240
IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;
```

When `protocolPaused == true`, fee minting is skipped:

```solidity
// contracts/LRTOracle.sol:243-247
uint256 protocolFeeInETH = 0;
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
```

But `rsETHPrice` is **unconditionally updated** to the new value regardless of pause state:

```solidity
// contracts/LRTOracle.sol:250, 313
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
// ... (price threshold checks) ...
rsETHPrice = newRsETHPrice;
```

The fee baseline for the next call is `previousTVL = rsethSupply.mulWad(rsETHPrice)`. Because `rsETHPrice` was already advanced to reflect the yield earned during the pause, the next call after unpausing sees `totalETHInProtocol ≈ previousTVL` and collects zero fee. The protocol fee for the entire pause window is permanently lost.

---

### Impact Explanation

Every time `updateRSETHPrice()` is called while `lrtDepositPool` or `withdrawalManager` is paused (but `LRTOracle` is not), the protocol treasury permanently forfeits the rsETH fee that should have been minted on the yield accrued during that window. The fee is not deferred — it is gone. This constitutes **theft of unclaimed yield** from the protocol treasury, matching the "High — Theft of unclaimed yield" impact tier.

---

### Likelihood Explanation

`LRTDepositPool` and `LRTWithdrawalManager` are paused independently of `LRTOracle` during routine security responses, maintenance, or EigenLayer-related incidents. `LRTOracle` is intentionally kept active during such pauses so that the price feed remains available. During any such pause window, `updateRSETHPrice()` is publicly callable by any EOA or contract, making the trigger trivially reachable with no special privileges. Likelihood is **Medium**.

---

### Recommendation

When `protocolPaused == true`, do not update `rsETHPrice`. Either return early before writing the new price, or revert. This preserves the fee baseline so that when the protocol is unpaused, the full yield accrued during the pause is subject to the normal fee calculation on the next `updateRSETHPrice()` call.

```solidity
if (protocolPaused) {
    return; // do not advance rsETHPrice; fee will be collected after unpause
}
```

---

### Proof of Concept

**Setup:**
- `rsethSupply = 1 000 rsETH`, `rsETHPrice = 1.05 ETH`, `protocolFeeInBPS = 1000` (10%)
- `previousTVL = 1 000 × 1.05 = 1 050 ETH`

**Step 1 — Partial pause:** `lrtDepositPool` is paused (e.g., security incident). `LRTOracle.paused = false`.

**Step 2 — Yield accrues:** EigenLayer rewards push `totalETHInProtocol` to `1 060 ETH` (10 ETH yield).

**Step 3 — Unprivileged call:** Any user calls `updateRSETHPrice()`.
- `whenNotPaused` passes (`LRTOracle.paused = false`).
- `protocolPaused = lrtDepositPool.paused() = true`.
- `protocolFeeInETH = 0` (fee skipped).
- `newRsETHPrice = 1 060 / 1 000 = 1.06 ETH`.
- `rsETHPrice` is written as `1.06 ETH`.

**Step 4 — Unpause:** `lrtDepositPool` is unpaused.

**Step 5 — Next price update:** `updateRSETHPrice()` is called.
- `previousTVL = 1 000 × 1.06 = 1 060 ETH`.
- `totalETHInProtocol ≈ 1 060 ETH` (no new yield since Step 3).
- `totalETHInProtocol ≤ previousTVL` → `protocolFeeInETH = 0`.

**Result:** The 10 ETH of yield earned during the pause generated **0 protocol fee** instead of the expected `10 × 10% = 1 ETH` worth of rsETH minted to the treasury. The loss is permanent and scales with both the duration of the pause and the yield rate. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L236-247)
```text
        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L249-250)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```
