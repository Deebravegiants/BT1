### Title
`updateRSETHPrice()` Permanently Reverts When `maxFeeMintAmountPerDay` Is Zero and Protocol Fees Are Due — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._checkAndUpdateDailyFeeMintLimit` assumes `maxFeeMintAmountPerDay` is non-zero whenever protocol fees are due, but this variable defaults to `0` and is never set during `initialize` or `reinitialize`. When TVL increases and `maxFeeMintAmountPerDay == 0`, every call to the public `updateRSETHPrice()` reverts, permanently freezing unclaimed protocol yield and allowing the rsETH price to go stale.

---

### Finding Description

The analog to the external report's `unwrap()` on `None` is the implicit assumption in `_checkAndUpdateDailyFeeMintLimit` that `maxFeeMintAmountPerDay` is non-zero when a fee amount is passed. The function performs a strict greater-than comparison:

```solidity
// LRTOracle.sol L205-L207
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
}
``` [1](#0-0) 

When `maxFeeMintAmountPerDay == 0` (its Solidity default) and `feeAmount > 0`, the condition `feeAmount > 0` is always true, so the function always reverts. `feeAmount > 0` occurs whenever `protocolFeeInETH > 0`, which happens whenever TVL increases and the protocol is not paused:

```solidity
// LRTOracle.sol L244-L247
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
``` [2](#0-1) 

The call chain is:

```
updateRSETHPrice() [public]
  → _updateRsETHPrice()
      → _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)  ← reverts
``` [3](#0-2) 

Critically, `maxFeeMintAmountPerDay` is **not initialized** in either `initialize` or `reinitialize`. It must be set separately via `setMaxFeeMintAmountPerDay`:

```solidity
// LRTOracle.sol L64-L68 (initialize)
function initialize(address lrtConfigAddr) external initializer {
    UtilLib.checkNonZeroAddress(lrtConfigAddr);
    lrtConfig = ILRTConfig(lrtConfigAddr);
    emit UpdatedLRTConfig(lrtConfigAddr);
}
``` [4](#0-3) 

```solidity
// LRTOracle.sol L72-L79 (reinitialize)
function reinitialize(uint256 _feePeriodStartTime) external reinitializer(2) onlyLRTManager {
    ...
    feePeriodStartTime = _feePeriodStartTime;
    // maxFeeMintAmountPerDay is NOT set here
}
``` [5](#0-4) 

The `remainingDailyFeeMintLimit()` view function correctly guards against `maxFeeMintAmountPerDay == 0`, but `_checkAndUpdateDailyFeeMintLimit` does not:

```solidity
// LRTOracle.sol L171
if (maxFeeMintAmountPerDay == 0) return 0;  // guard present in view function only
``` [6](#0-5) 

This inconsistency is the direct analog to the external report: the view path handles the zero case, but the write path does not — exactly as `view.rs` assumed `posted_order` was non-empty while the execution path did not enforce it.

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

While `maxFeeMintAmountPerDay == 0`, every call to `updateRSETHPrice()` reverts whenever TVL has grown. The protocol fee (`protocolFeeInBPS` of all yield) is never minted to the treasury. The yield accrued during this window is permanently unrecoverable — the fee is not retroactively minted once the variable is set. Additionally, the stale rsETH price allows new depositors to receive more rsETH than they are entitled to at the expense of existing holders, constituting a secondary share-dilution impact.

---

### Likelihood Explanation

`maxFeeMintAmountPerDay` is `0` by default and is absent from both `initialize` and `reinitialize`. Any deployment or upgrade that does not explicitly call `setMaxFeeMintAmountPerDay` immediately after will be in this broken state. The trigger is entirely unprivileged: any external caller invoking `updateRSETHPrice()` (a public, permissionless function) after TVL has increased will hit the revert. No malicious intent is required — a legitimate price-update call is sufficient, mirroring the external report's "legitimate payload causes crash" pattern.

---

### Recommendation

Add a zero-guard in `_checkAndUpdateDailyFeeMintLimit` consistent with the existing guard in `remainingDailyFeeMintLimit`:

```solidity
function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
+   if (maxFeeMintAmountPerDay == 0) return; // limit not configured; skip enforcement
    ...
}
```

Alternatively, require `maxFeeMintAmountPerDay` to be set during `initialize` / `reinitialize` so the invariant is enforced at deployment time.

---

### Proof of Concept

1. Deploy `LRTOracle` (or upgrade it via `reinitialize`) without calling `setMaxFeeMintAmountPerDay`. `maxFeeMintAmountPerDay` remains `0`.
2. Users deposit assets into `LRTDepositPool`, increasing TVL above the previous `rsETHPrice × rsETHSupply`.
3. Any user (or keeper bot) calls `updateRSETHPrice()`.
4. Inside `_updateRsETHPrice`, `totalETHInProtocol > previousTVL`, so `protocolFeeInETH > 0`.
5. `rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice) > 0`.
6. `_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)` evaluates `0 + rsethAmountToMintAsProtocolFee > 0` → **reverts with `DailyFeeMintLimitExceeded`**.
7. `updateRSETHPrice()` reverts. The rsETH price is not updated. Protocol fee is not minted. This repeats on every subsequent call as long as `maxFeeMintAmountPerDay == 0`.

### Citations

**File:** contracts/LRTOracle.sol (L64-68)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

**File:** contracts/LRTOracle.sol (L72-79)
```text
    function reinitialize(uint256 _feePeriodStartTime) external reinitializer(2) onlyLRTManager {
        if (_feePeriodStartTime > block.timestamp || _feePeriodStartTime <= block.timestamp - 1 days) {
            revert PeriodStartTimeShouldBeWithin24Hours();
        }

        feePeriodStartTime = _feePeriodStartTime;
        emit FeePeriodStartTimeSet(_feePeriodStartTime);
    }
```

**File:** contracts/LRTOracle.sol (L171-171)
```text
        if (maxFeeMintAmountPerDay == 0) return 0;
```

**File:** contracts/LRTOracle.sol (L205-207)
```text
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }
```

**File:** contracts/LRTOracle.sol (L244-247)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L299-311)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }
```
