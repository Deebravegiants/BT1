Audit Report

## Title
DoS on `updateRSETHPrice()` When `maxFeeMintAmountPerDay == 0` and TVL Increases — (`contracts/LRTOracle.sol`)

## Summary

`_checkAndUpdateDailyFeeMintLimit` in `LRTOracle` has no guard for `maxFeeMintAmountPerDay == 0`. When this variable is zero (its default uninitialized value) and a non-zero protocol fee is computed, the daily-limit check always reverts with `DailyFeeMintLimitExceeded`. Because `FeeReceiver.sendFunds()` and `LRTOracle.updateRSETHPrice()` are both permissionless, any caller can force TVL to increase and then trigger the revert, freezing the price oracle until an admin reconfigures the limit.

## Finding Description

**Root cause — missing zero-guard in `_checkAndUpdateDailyFeeMintLimit`:**

`LRTOracle.sol` L205:
```solidity
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(...);
}
```
When `maxFeeMintAmountPerDay == 0` (the default for an uninitialized `uint256`, L35) and `feeAmount > 0`, the condition evaluates to `feeAmount > 0` → always `true` → always reverts. [1](#0-0) 

**Inconsistency with the view function:** `remainingDailyFeeMintLimit()` (L171) explicitly returns `0` when `maxFeeMintAmountPerDay == 0`, signalling that zero is a valid/disabled state — but the enforcement function does not honour that semantics. [2](#0-1) 

**`maxFeeMintAmountPerDay` is 0 by default** and can be explicitly reset to 0 by a manager via `setMaxFeeMintAmountPerDay`. [3](#0-2) 

**`FeeReceiver.sendFunds()` is permissionless** — no role check, forwards all ETH to `LRTDepositPool.receiveFromRewardReceiver()`, which increases `address(this).balance` and therefore `totalETHInProtocol`. [4](#0-3) [5](#0-4) 

**ETH balance is counted in TVL:** `getETHDistributionData()` returns `ethLyingInDepositPool = address(this).balance`, which flows through `getTotalAssetDeposits(ETH_TOKEN)` → `_getTotalEthInProtocol()`. [6](#0-5) 

**Fee computation path:** When `!protocolPaused && totalETHInProtocol > previousTVL` and `lrtConfig.protocolFeeInBPS() > 0`, a non-zero `protocolFeeInETH` is computed, which leads to `_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)` being called and reverting. [7](#0-6) [8](#0-7) 

**`updateRSETHPrice()` is permissionless** (only `whenNotPaused`), so any caller can trigger the revert. [9](#0-8) 

## Impact Explanation

`rsETHPrice` cannot be updated while `maxFeeMintAmountPerDay == 0` and any TVL growth exists. Downstream contracts that gate deposits or withdrawals on a fresh oracle price (e.g., `LRTWithdrawalManager.getExpectedAssetAmount` reads `lrtOracle.rsETHPrice()`) will operate on a stale price. An admin can unblock by calling `setMaxFeeMintAmountPerDay` with a non-zero value, so the freeze is **temporary**, not permanent.

**Correct scope: Medium — Temporary freezing of funds.** [10](#0-9) 

## Likelihood Explanation

- `maxFeeMintAmountPerDay` is `0` by default before any manager sets it, making this reachable in the early deployment window or after an explicit reset to zero.
- Both trigger calls (`FeeReceiver.sendFunds()` and `LRTOracle.updateRSETHPrice()`) require no privileges.
- `protocolFeeInBPS > 0` is the normal production configuration (`LRTConfig.setProtocolFeeBps` allows up to 1500 BPS).
- Likelihood is **medium**: requires a specific but realistic configuration state (uninitialized or reset `maxFeeMintAmountPerDay`). [11](#0-10) 

## Recommendation

Add an early-exit in `_checkAndUpdateDailyFeeMintLimit` when `maxFeeMintAmountPerDay == 0`, treating zero as "fee minting disabled / no limit enforced":

```solidity
function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
    if (maxFeeMintAmountPerDay == 0) return; // fee minting disabled; skip limit check
    // ... existing logic
}
```

Alternatively, if zero is intended to mean "no fee minting allowed at all", then `_updateRsETHPrice` should skip the fee computation entirely when `maxFeeMintAmountPerDay == 0`, rather than computing a fee and then failing the limit check. [1](#0-0) 

## Proof of Concept

```
Preconditions:
  maxFeeMintAmountPerDay = 0  (default uninitialized state)
  protocolFeeInBPS > 0        (normal production config)
  FeeReceiver holds 1 ETH
  Protocol not paused
  ETH_TOKEN is a supported asset

Step 1: attacker calls FeeReceiver.sendFunds()
  → 1 ETH forwarded to LRTDepositPool via receiveFromRewardReceiver{ value: 1 ether }()
  → LRTDepositPool.address(this).balance increases by 1 ETH
  → getETHDistributionData().ethLyingInDepositPool increases
  → _getTotalEthInProtocol() returns a higher value

Step 2: attacker calls LRTOracle.updateRSETHPrice()
  → totalETHInProtocol > previousTVL
  → rewardAmount = totalETHInProtocol - previousTVL > 0
  → protocolFeeInETH = (rewardAmount * protocolFeeInBPS) / 10_000 > 0
  → rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice) > 0
  → _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)
  → 0 + rsethAmountToMintAsProtocolFee > 0 == true
  → revert DailyFeeMintLimitExceeded(rsethAmountToMintAsProtocolFee, 0)

Result: rsETHPrice is never updated; oracle is frozen until admin calls
        setMaxFeeMintAmountPerDay with a non-zero value.

Foundry test sketch:
  1. Deploy protocol with protocolFeeInBPS = 500 (5%), maxFeeMintAmountPerDay = 0
  2. Seed FeeReceiver with 1 ether (vm.deal)
  3. vm.prank(attacker); feeReceiver.sendFunds();
  4. vm.expectRevert(LRTOracle.DailyFeeMintLimitExceeded.selector);
     vm.prank(attacker); lrtOracle.updateRSETHPrice();
```

### Citations

**File:** contracts/LRTOracle.sol (L35-35)
```text
    uint256 public maxFeeMintAmountPerDay;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L132-135)
```text
    function setMaxFeeMintAmountPerDay(uint256 _maxFeeMintAmountPerDay) external onlyLRTManager {
        maxFeeMintAmountPerDay = _maxFeeMintAmountPerDay;
        emit MaxFeeMintAmountPerDayUpdated(_maxFeeMintAmountPerDay);
    }
```

**File:** contracts/LRTOracle.sol (L170-172)
```text
    function remainingDailyFeeMintLimit() external view returns (uint256) {
        if (maxFeeMintAmountPerDay == 0) return 0;

```

**File:** contracts/LRTOracle.sol (L197-210)
```text
    function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
        // Reset the period if it's unset or a day has passed
        if (block.timestamp >= feePeriodStartTime + 1 days) {
            currentPeriodMintedFeeAmount = 0;
            feePeriodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
    }
```

**File:** contracts/LRTOracle.sol (L244-247)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L299-303)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
```

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTDepositPool.sol (L61-61)
```text
    function receiveFromRewardReceiver() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTConfig.sol (L196-199)
```text
    function setProtocolFeeBps(uint256 _protocolFeeInBPS) external onlyRole(LRTConstants.MANAGER) {
        if (_protocolFeeInBPS > 1500) revert ProtocolFeeExceedsLimit();
        protocolFeeInBPS = _protocolFeeInBPS;
        emit UpdateFee(_protocolFeeInBPS);
```
