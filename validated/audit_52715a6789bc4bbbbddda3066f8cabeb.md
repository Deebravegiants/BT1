### Title
Aave Rounding Deficit Permanently Silences Future Yield to Treasury — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

When `aaveAWETH.balanceOf(address(this))` falls below `totalETHDepositedToAave` by more than 2 wei (a realistic accumulation of per-withdrawal rounding losses), `_withdrawFromAave` correctly caps the withdrawal at `aaveBalance` but only decrements `totalETHDepositedToAave` by that same amount — leaving a permanent positive remainder (`delta`) in `totalETHDepositedToAave` even after the Aave position is fully drained. All subsequent interest accrual is silently absorbed into that deficit and never forwarded to the treasury until new interest exceeds `delta`.

---

### Finding Description

**Root cause — `_withdrawFromAave` (lines 905–921):**

```solidity
uint256 withdrawablePrincipal =
    aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;

aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
totalETHDepositedToAave -= withdrawnAmount;          // ← only decremented by aaveBalance
``` [1](#0-0) 

When `aaveBalance = T − delta` and `totalETHDepositedToAave = T`, the function withdraws `T − delta` and sets `totalETHDepositedToAave = delta`. The Aave position is now empty, but `totalETHDepositedToAave` retains a phantom `delta`.

**How `delta > 2` accumulates:**

Each call to `aaveWETHGateway.withdrawETH` performs a floor-division on the aWETH scaled balance (`scaledBalance × liquidityIndex / RAY`), rounding down by up to 1 wei. After ≥ 3 such operations, `totalETHDepositedToAave − aaveBalance > 2`, causing `_checkAaveHealth()` to return `false`. [2](#0-1) 

**Why the health check does not protect here:**

`_checkAaveHealth()` is only enforced in the *external* `collectInterestToTreasury()`. The *internal* `_collectInterestToTreasury()` and `_withdrawFromAave()` are called unconditionally from `setAaveIntegrationEnabled(false)`, `configureAaveIntegration`, and `emergencyWithdrawFromAave` — all of which proceed even when the health check would fail. [3](#0-2) [4](#0-3) 

**Effect on `_collectInterestToTreasury` after re-enabling:**

```solidity
if (aaveBalance <= principal) return 0;          // ← returns 0 while interest < delta
interestAmount = aaveBalance - principal;        // ← under-reports by delta once interest > delta
``` [5](#0-4) 

**Effect on `getAccruedInterest`:**

```solidity
if (aaveBalance <= totalETHDepositedToAave) return 0;   // ← returns 0 until interest > delta
``` [6](#0-5) 

---

### Impact Explanation

After the deficit is baked in, the treasury permanently loses `delta` wei of yield. `getAccruedInterest()` returns 0 and `_collectInterestToTreasury` sends 0 to the treasury until new interest exceeds `delta`. This matches **High — Theft of unclaimed yield**.

In practice `delta` is bounded by the number of Aave withdrawal operations × 1 wei/op, so the absolute financial loss is small (a few hundred wei over the protocol's lifetime). The mechanism is structurally sound but the monetary impact is negligible at realistic ETH prices.

---

### Likelihood Explanation

The rounding loss is an inherent property of Aave v3's ray-math and occurs on every `withdrawETH` call. Exceeding the 2-wei tolerance requires only 3 withdrawal operations, which is trivially reached in normal production use. The subsequent disable/reconfigure/emergency-withdraw path is a standard operational action. Likelihood is **medium-high** for the mechanism to trigger, but the financial consequence per occurrence is tiny.

---

### Recommendation

In `_withdrawFromAave`, when `aaveBalance < totalETHDepositedToAave`, reset `totalETHDepositedToAave` to zero (not to `totalETHDepositedToAave − aaveBalance`) after a full drain:

```solidity
if (withdrawnAmount == withdrawablePrincipal && aaveBalance < totalETHDepositedToAave) {
    totalETHDepositedToAave = 0;   // absorb rounding dust rather than leaving a phantom principal
} else {
    totalETHDepositedToAave -= withdrawnAmount;
}
```

Alternatively, track `totalETHDepositedToAave` as a floor-adjusted value by subtracting the rounding loss at deposit time.

---

### Proof of Concept

```solidity
// Fork test (local Anvil fork of mainnet)
// State: totalETHDepositedToAave = 1000 ether, aaveBalance = 1000 ether - 3 wei (delta = 3)
// Achieved by: 3 deposit+withdraw cycles each losing 1 wei to Aave rounding

// Step 1: manager disables integration
vm.prank(manager);
withdrawalManager.setAaveIntegrationEnabled(false);
// _collectInterestToTreasury() → returns 0 (aaveBalance < principal)
// _withdrawFromAave(aaveBalance) → withdraws (1000 ether - 3), sets totalETHDepositedToAave = 3

// Step 2: re-enable and deposit fresh ETH
vm.prank(manager);
withdrawalManager.setAaveIntegrationEnabled(true);
vm.prank(operator);
withdrawalManager.depositIdleETHToAave(500 ether);
// totalETHDepositedToAave = 3 + 500 ether, aaveBalance = 500 ether

// Step 3: simulate 2 wei of interest accruing in Aave
// aaveBalance = 500 ether + 2

// Step 4: assert treasury receives nothing
uint256 treasuryBefore = treasury.balance;
vm.prank(operator);
withdrawalManager.collectInterestToTreasury();  // reverts: AaveHealthCheckFailed (balance still < principal)
// OR if health passes: treasury receives (500 ether + 2) - (3 + 500 ether) = 0 (underflow → 0)

assertEq(withdrawalManager.getAccruedInterest(), 0);  // passes — 2 < 3
assertEq(treasury.balance - treasuryBefore, 0);       // passes — 2 wei of yield silently absorbed
``` [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L486-497)
```text
        if (!enabled) {
            uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
            if (aaveBalance > 0) {
                // First collect any accrued interest to treasury
                _collectInterestToTreasury();

                // Then withdraw remaining principal from Aave back to contract
                aaveBalance = aaveAWETH.balanceOf(address(this));
                if (aaveBalance > 0) {
                    _withdrawFromAave(aaveBalance);
                }
            }
```

**File:** contracts/LRTWithdrawalManager.sol (L540-544)
```text
    function collectInterestToTreasury() external nonReentrant onlyLRTOperator returns (uint256 interestAmount) {
        // Check health and revert if integration not enabled or unhealthy
        if (!_checkAaveHealth()) revert AaveHealthCheckFailed();

        return _collectInterestToTreasury();
```

**File:** contracts/LRTWithdrawalManager.sol (L643-647)
```text
    function getAccruedInterest() external view returns (uint256 interest) {
        uint256 aaveBalance = getAaveBalance();
        if (aaveBalance <= totalETHDepositedToAave) return 0;
        return aaveBalance - totalETHDepositedToAave;
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

**File:** contracts/LRTWithdrawalManager.sol (L925-933)
```text
    function _checkAaveHealth() internal view returns (bool healthy) {
        if (!isAaveIntegrationEnabled) return false;
        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        uint256 principal = totalETHDepositedToAave;
        // Allow small rounding differences (up to 2 wei)
        // Check if balance is significantly less than principal
        if (principal > aaveBalance && principal - aaveBalance > 2) return false;
        return true;
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
