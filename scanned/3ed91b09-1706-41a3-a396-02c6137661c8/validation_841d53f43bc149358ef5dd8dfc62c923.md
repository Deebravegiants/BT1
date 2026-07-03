I have all the code needed. Let me trace through the exact scenario carefully.

### Title
Residual `totalETHDepositedToAave` After Full Withdrawal Permanently Breaks Aave Accounting, Temporarily Freezing ETH Withdrawal Completions — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`_withdrawFromAave` caps the amount withdrawn at `min(aaveBalance, totalETHDepositedToAave)`. When Aave's rebasing aToken rounds the balance down by 1–2 wei (a condition the contract itself explicitly tolerates in `_checkAaveHealth`), a full withdrawal leaves `totalETHDepositedToAave` with a non-zero residual while `aaveBalance` reaches zero. Every subsequent call to `_withdrawFromAave` then reverts with `InsufficientAaveBalance`, blocking all ETH withdrawal completions until an admin manually disables the Aave integration.

---

### Finding Description

`_checkAaveHealth` explicitly permits up to 2 wei of divergence between `aaveAWETH.balanceOf(address(this))` and `totalETHDepositedToAave`: [1](#0-0) 

`_withdrawFromAave` computes the withdrawable amount as: [2](#0-1) 

When `aaveBalance = N - 1` and `totalETHDepositedToAave = N` (a 1-wei rounding difference within the tolerated range):

| Step | Value |
|---|---|
| `withdrawablePrincipal` | `min(N-1, N) = N-1` |
| `withdrawnAmount` | `min(N, N-1) = N-1` |
| aWETH burned by gateway | `N-1` → `aaveBalance = 0` |
| `totalETHDepositedToAave -= N-1` | **residual = 1** |

After this call: `aaveBalance == 0` but `totalETHDepositedToAave == 1`. Any subsequent `_withdrawFromAave` call hits the guard at line 909 and reverts: [3](#0-2) 

There is no code path that can reset `totalETHDepositedToAave` to zero without a contract upgrade, because every write to it goes through `_depositToAave` (increments) or `_withdrawFromAave` (decrements, but that now reverts).

---

### Impact Explanation

`_processWithdrawalCompletion` calls `_withdrawFromAave` whenever the contract's ETH balance is insufficient to cover a pending ETH withdrawal request and Aave integration is enabled: [4](#0-3) 

Once the residual state is reached, every such call reverts with `InsufficientAaveBalance`, blocking all ETH withdrawal completions. The freeze persists until the LRT Manager calls `setAaveIntegrationEnabled(false)`. This is a **temporary freeze of user funds** (Medium), not permanent, because admin intervention can unblock it — but the accounting corruption (`totalETHDepositedToAave > 0` with zero aWETH) is permanent without an upgrade.

---

### Likelihood Explanation

Aave v3 aToken balances are known to round down by 1 wei due to ray-precision interest index arithmetic. The contract's own `_checkAaveHealth` explicitly documents and tolerates this (up to 2 wei). The precondition is therefore a normal operating condition, not an edge case. Any full withdrawal of the Aave position after even a single block of interest accrual can trigger this.

---

### Recommendation

When `withdrawnAmount == aaveBalance` (i.e., the entire aWETH balance is being withdrawn), zero out `totalETHDepositedToAave` unconditionally rather than subtracting:

```solidity
if (withdrawnAmount >= aaveBalance) {
    totalETHDepositedToAave = 0;
} else {
    totalETHDepositedToAave -= withdrawnAmount;
}
```

This ensures that draining all aWETH always resets the principal tracker to zero, regardless of sub-wei rounding.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

// Mock gateway that always delivers 1 wei less than requested
contract MockGateway {
    function withdrawETH(address, uint256 amount, address to) external {
        // Burns amount aWETH but delivers amount-1 ETH
        payable(to).transfer(amount - 1);
    }
    function depositETH(address, address, uint16) external payable {}
    receive() external payable {}
}

// Mock aWETH that tracks balance manually
contract MockAWETH {
    mapping(address => uint256) public balanceOf;
    function mint(address to, uint256 amount) external { balanceOf[to] += amount; }
    // Gateway burns exactly withdrawnAmount aWETH
    function burn(address from, uint256 amount) external { balanceOf[from] -= amount; }
}

// Test:
// 1. depositToAave(100 ether) → totalETHDepositedToAave = 100e18
// 2. Simulate 1 wei rounding: mockAWETH.balanceOf = 100e18 - 1
// 3. _withdrawFromAave(100e18):
//    withdrawablePrincipal = 100e18 - 1
//    withdrawnAmount = 100e18 - 1
//    gateway burns 100e18-1 aWETH → aaveBalance = 0
//    totalETHDepositedToAave -= (100e18-1) → totalETHDepositedToAave = 1
// 4. assert(aaveAWETH.balanceOf(withdrawalManager) == 0)
// 5. assert(totalETHDepositedToAave == 1)  // BUG: should be 0
// 6. _withdrawFromAave(1) → reverts InsufficientAaveBalance  // FREEZE
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L720-724)
```text
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
            uint256 contractBalance = address(this).balance;
            if (contractBalance < request.expectedAssetAmount) {
                uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
                _withdrawFromAave(amountNeeded);
```

**File:** contracts/LRTWithdrawalManager.sol (L908-909)
```text
        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();
```

**File:** contracts/LRTWithdrawalManager.sol (L912-918)
```text
        uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

        withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
        if (withdrawnAmount == 0) return 0;

        aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
        totalETHDepositedToAave -= withdrawnAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L929-931)
```text
        // Allow small rounding differences (up to 2 wei)
        // Check if balance is significantly less than principal
        if (principal > aaveBalance && principal - aaveBalance > 2) return false;
```
