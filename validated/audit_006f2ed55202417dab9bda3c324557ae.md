### Title
Withdrawal Payout Capped at Initiation-Time Value Causes Systematic Loss of Yield Accrued During Delay - (`contracts/LRTWithdrawalManager.sol`)

### Summary

In `LRTWithdrawalManager._calculatePayoutAmount()`, the payout to a withdrawing user is always capped at the `expectedAssetAmount` recorded at initiation time. Because rsETH is a yield-bearing token whose price monotonically increases as staking rewards accrue, the `currentReturn` computed at unlock time will routinely exceed `expectedAssetAmount`. The function computes `currentReturn` but discards it in favour of the stale initiation-time value, burning the user's full rsETH while paying out less than it is worth. The yield that accrued during the withdrawal delay is permanently lost to the user.

### Finding Description

When a user calls `initiateWithdrawal()`, the contract records `expectedAssetAmount` using the rsETH price at that moment:

```solidity
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
// ...
withdrawalRequests[requestId] = WithdrawalRequest({
    rsETHUnstaked: rsETHUnstaked,
    expectedAssetAmount: expectedAssetAmount,
    withdrawalStartBlock: block.number
});
``` [1](#0-0) 

At unlock time, `_calculatePayoutAmount` computes the current fair value of the rsETH but then returns the **minimum** of the two:

```solidity
function _calculatePayoutAmount(...) private view returns (uint256) {
    uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
    return (request.expectedAssetAmount < currentReturn)
        ? request.expectedAssetAmount   // <-- currentReturn computed but discarded
        : currentReturn;
}
``` [2](#0-1) 

`_unlockWithdrawalRequests` then burns the **full** `rsETHUnstaked` amount while only unlocking `payoutAmount` (the minimum) from the vault:

```solidity
assetsCommitted[asset] -= request.expectedAssetAmount;
request.expectedAssetAmount = payoutAmount;   // overwritten with minimum
rsETHAmountToBurn += request.rsETHUnstaked;   // full rsETH burned
assetAmountToUnlock += payoutAmount;           // only minimum unlocked
``` [3](#0-2) 

The full rsETH is subsequently burned:

```solidity
if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
unstakingVault.redeem(asset, assetAmountUnlocked);
``` [4](#0-3) 

The structural parallel to the external report is exact: `currentReturn` is computed (analogous to `amountScaled`) but silently discarded when it exceeds `expectedAssetAmount`, and the user receives the unscaled initiation-time value instead of the yield-adjusted amount.

### Impact Explanation

rsETH is explicitly designed to appreciate over time as EigenLayer staking rewards accrue; `LRTOracle.updateRSETHPrice()` is called regularly to reflect this. The default withdrawal delay is 8 days (`withdrawalDelayBlocks = 8 days / 12 seconds`). [5](#0-4) 

During those 8 days the user's rsETH continues to appreciate, but the payout is frozen at the initiation-time price. The full rsETH is burned, yet the user receives less than its current worth. The difference remains in the unstaking vault and is effectively redistributed to future withdrawers — constituting a direct, permanent loss of yield for the initiating user.

**Impact**: High — theft of unclaimed yield. Every withdrawal where rsETH price rose during the delay (the normal case) results in the user losing the yield that accrued over the delay window.

### Likelihood Explanation

rsETH price increases are the expected, routine outcome of the protocol operating correctly. Any user who calls `initiateWithdrawal()` and then `completeWithdrawal()` after the 8-day delay will be affected whenever `updateRSETHPrice()` has been called in the interim — which operators are incentivised to do regularly. No special conditions, attacker capital, or privileged access are required; the loss is automatic for every ordinary withdrawer.

### Recommendation

Replace the `min` logic with a calculation that pays the user the **current** fair value of their rsETH at unlock time, not the stale initiation-time estimate:

```solidity
function _calculatePayoutAmount(...) private view returns (uint256) {
    uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
    return currentReturn; // always pay current fair value
}
```

If a cap is desired for slippage protection, apply it symmetrically (e.g., cap at a small percentage above `expectedAssetAmount`) rather than hard-capping at the initiation-time value.

### Proof of Concept

1. rsETH price at `t=0`: 1.05 ETH/rsETH. User initiates withdrawal of 100 rsETH for stETH. `expectedAssetAmount` ≈ 100 × 1.05 / 1.0 = 105 stETH.
2. 8 days pass. `updateRSETHPrice()` is called; rsETH price is now 1.06 ETH/rsETH (normal yield accrual).
3. Operator calls `unlockQueue`. `currentReturn` = 100 × 1.06 / 1.0 = 106 stETH. Since `105 < 106`, `payoutAmount = 105`.
4. 100 rsETH is burned; user receives 105 stETH instead of 106 stETH. The 1 stETH of yield accrued during the delay is permanently lost to the user.
5. The gap grows with larger withdrawals and longer delays (up to 16 days maximum). [6](#0-5)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L168-175)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L305-307)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L580-593)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L802-808)
```text
            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;

```

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
    }
```
