### Title
`_withdrawFromAave` Principal Cap Causes `completeWithdrawal` to Always Revert When Aave Interest Exceeds Withdrawal Shortfall — (`File: contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager._withdrawFromAave` hard-caps every Aave redemption at `totalETHDepositedToAave` (the tracked principal). Once Aave interest accrues, the actual aWETH balance exceeds the principal. Any user ETH withdrawal whose shortfall is larger than the remaining principal — but smaller than the full Aave balance — will always revert with `InsufficientLiquidityForWithdrawal`, even though sufficient ETH exists in Aave to satisfy the request.

---

### Finding Description

`LRTWithdrawalManager` optionally deposits unlocked ETH into Aave v3 to earn yield. When a user calls `completeWithdrawal(ETH_TOKEN, ...)`, `_processWithdrawalCompletion` checks whether the contract's raw ETH balance covers the request; if not, it calls `_withdrawFromAave(amountNeeded)`.

`_withdrawFromAave` computes:

```solidity
// Only withdraw up to the principal amount (don't use accrued interest for user withdrawals)
uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave
    ? aaveBalance
    : totalETHDepositedToAave;                          // ← always ≤ principal

withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
``` [1](#0-0) 

When Aave interest has accrued, `aaveBalance > totalETHDepositedToAave`, so `withdrawablePrincipal = totalETHDepositedToAave`. The function therefore silently withdraws less than `amountNeeded`.

Back in `_processWithdrawalCompletion`, the post-withdrawal guard then fires:

```solidity
uint256 balanceAfter = address(this).balance;
if (balanceAfter < request.expectedAssetAmount) {
    revert InsufficientLiquidityForWithdrawal();
}
``` [2](#0-1) 

Because `_withdrawFromAave` returned less than `amountNeeded`, `balanceAfter` is still below `request.expectedAssetAmount`, and the revert is guaranteed — even though the full Aave balance (principal + interest) would have been sufficient.

The `_collectInterestToTreasury` helper does not update `totalETHDepositedToAave`, so calling it first does not fix the shortfall; it only reduces `aaveBalance` back to the principal, leaving the user in the same blocked state. [3](#0-2) 

---

### Impact Explanation

**Medium — Temporary freezing of user ETH withdrawal funds.**

Any rsETH holder who has a queued and unlocked ETH withdrawal request is unable to complete it whenever:

- `isAaveIntegrationEnabled == true`, and
- `address(this).balance < request.expectedAssetAmount`, and
- `request.expectedAssetAmount - address(this).balance > totalETHDepositedToAave` (shortfall exceeds tracked principal), yet
- `request.expectedAssetAmount - address(this).balance ≤ aaveAWETH.balanceOf(address(this))` (full Aave balance is sufficient).

The user's rsETH has already been burned at `unlockQueue` time; they cannot re-enter the queue. Their ETH is frozen until an operator manually calls `emergencyWithdrawFromAave` or deposits additional ETH to Aave to raise `totalETHDepositedToAave`.

---

### Likelihood Explanation

**Medium.** Aave interest accrues continuously and automatically. The longer the integration is active, the larger the gap between `aaveBalance` and `totalETHDepositedToAave`. Any user whose withdrawal shortfall falls in the range `(totalETHDepositedToAave, aaveBalance]` is affected. This is a normal operating condition, not an edge case.

---

### Recommendation

Remove the artificial principal cap from `_withdrawFromAave` when the purpose is to service user withdrawals. The cap was introduced to preserve interest for the treasury, but it incorrectly blocks legitimate user redemptions. Instead, allow the full `aaveBalance` to be used for user withdrawals and separately account for interest:

```solidity
// Use full aave balance for user withdrawals; interest accounting is separate
withdrawnAmount = amount > aaveBalance ? aaveBalance : amount;
```

Alternatively, before capping, check whether the full balance (including interest) is needed to satisfy the request, and only then allow drawing on interest. The `totalETHDepositedToAave` tracker should be updated accordingly after any interest-inclusive withdrawal.

---

### Proof of Concept

**Setup:**
1. Aave integration is enabled. 100 ETH has been deposited to Aave. `totalETHDepositedToAave = 100 ETH`.
2. Aave accrues 5 ETH interest. `aaveAWETH.balanceOf(address(this)) = 105 ETH`. `totalETHDepositedToAave` remains `100 ETH`.
3. `address(this).balance = 0` (all ETH is in Aave).
4. A user has an unlocked withdrawal request for `101 ETH`.

**Execution of `completeWithdrawal(ETH_TOKEN, ...)`:**

```
_processWithdrawalCompletion:
  contractBalance = address(this).balance = 0
  amountNeeded    = 101 - 0 = 101 ETH

_withdrawFromAave(101):
  aaveBalance          = 105 ETH
  withdrawablePrincipal = min(105, 100) = 100 ETH   ← capped at principal
  withdrawnAmount       = min(101, 100) = 100 ETH
  → withdraws 100 ETH, totalETHDepositedToAave = 0

back in _processWithdrawalCompletion:
  balanceAfter = 0 + 100 = 100 ETH
  100 < 101  →  revert InsufficientLiquidityForWithdrawal  ✗
```

The withdrawal fails. Yet 105 ETH was available in Aave — 4 ETH more than needed. The user's funds are frozen. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L719-731)
```text
        // If Aave integration is enabled and asset is ETH, withdraw from Aave if needed
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
            uint256 contractBalance = address(this).balance;
            if (contractBalance < request.expectedAssetAmount) {
                uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
                _withdrawFromAave(amountNeeded);

                // Verify we have sufficient balance after withdrawal
                uint256 balanceAfter = address(this).balance;
                if (balanceAfter < request.expectedAssetAmount) {
                    revert InsufficientLiquidityForWithdrawal();
                }
            }
```

**File:** contracts/LRTWithdrawalManager.sol (L905-921)
```text
    function _withdrawFromAave(uint256 amount) internal returns (uint256 withdrawnAmount) {
        if (amount == 0) return 0;

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // Only withdraw up to the principal amount (don't use accrued interest for user withdrawals)
        uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

        withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
        if (withdrawnAmount == 0) return 0;

        aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
        totalETHDepositedToAave -= withdrawnAmount;

        emit ETHWithdrawnFromAave(withdrawnAmount, totalETHDepositedToAave);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L945-961)
```text
    function _collectInterestToTreasury() internal returns (uint256 interestAmount) {
        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        uint256 principal = totalETHDepositedToAave;

        // Return 0 if no interest or balance is less than principal (accounting for rounding)
        if (aaveBalance <= principal) return 0;

        interestAmount = aaveBalance - principal;

        aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this));

        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        (bool sent,) = payable(treasury).call{ value: interestAmount }("");
        if (!sent) revert TreasuryTransferFailed();

        emit InterestCollectedToTreasury(interestAmount, treasury);
    }
```
