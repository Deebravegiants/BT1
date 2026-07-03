### Title
Users Can Be Left With Unwithdrawable rsETH Dust Due to Minimum Withdrawal Enforcement - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager` enforces a per-asset minimum rsETH amount for every withdrawal request. Neither `initiateWithdrawal` nor `instantWithdrawal` contains an exception for a user withdrawing their entire remaining balance. A user who makes a partial withdrawal that leaves a remainder below `minRsEthAmountToWithdraw[asset]` will be permanently unable to redeem that remainder through any withdrawal path.

### Finding Description
`LRTWithdrawalManager` stores a per-asset minimum in `minRsEthAmountToWithdraw[asset]` and enforces it unconditionally in both withdrawal entry points:

`initiateWithdrawal` (line 162):
```solidity
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
```

`instantWithdrawal` (line 224):
```solidity
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
```

Neither check has a bypass for the case where `rsETHUnstaked == IERC20(rsETH).balanceOf(msg.sender)` (i.e., the user is withdrawing their full remaining balance). There is no alternative withdrawal path in the contract that skips this check.

The minimum is set by the admin via `setMinRsEthAmountToWithdraw` and can be any non-zero value. Once a user's rsETH balance falls below this threshold — which can happen naturally after any partial withdrawal — both `initiateWithdrawal` and `instantWithdrawal` will revert for that user on that asset, with no recourse within the contract.

### Impact Explanation
**Medium — Temporary freezing of funds.**

A user's rsETH tokens represent a claim on underlying ETH/LST assets held by the protocol. If the user's remaining rsETH balance is below `minRsEthAmountToWithdraw[asset]`, those tokens cannot be redeemed through any on-chain path. The user's funds are effectively frozen until they acquire additional rsETH (from the open market or by making a new deposit) to bring their balance above the minimum, incurring extra costs. This is a direct availability impact on user funds that the user did not necessarily create intentionally.

### Likelihood Explanation
**Medium.**

Any user who makes a partial withdrawal — a completely normal and expected action — risks landing in this state. The minimum threshold is admin-configurable and can be set to any value. The scenario requires no special permissions, no front-running, and no external protocol failure. It is a natural consequence of the interaction between partial withdrawals and the unconditional minimum check.

### Recommendation
Add an exception to the minimum check in both `initiateWithdrawal` and `instantWithdrawal` that allows a user to withdraw their entire remaining rsETH balance even if it is below the configured minimum:

```solidity
uint256 userBalance = IERC20(lrtConfig.rsETH()).balanceOf(msg.sender);
if (rsETHUnstaked == 0 ||
    (rsETHUnstaked < minRsEthAmountToWithdraw[asset] && rsETHUnstaked != userBalance)) {
    revert InvalidAmountToWithdraw();
}
```

This mirrors the mitigation recommended in the analogous Ondo Finance finding: allow users to remove all their funds even if the amount falls below the minimum limit.

### Proof of Concept

1. Admin sets `minRsEthAmountToWithdraw[ETH]` = 1 rsETH via `setMinRsEthAmountToWithdraw`.
2. Alice deposits 2 ETH via `LRTDepositPool.depositETH`, receiving 2 rsETH.
3. Alice calls `initiateWithdrawal(ETH, 1.5e18, ...)`. This succeeds (1.5 > 1 minimum). Alice now holds 0.5 rsETH.
4. Alice calls `initiateWithdrawal(ETH, 0.5e18, ...)`. The check at line 162 evaluates `0.5e18 < 1e18` → `true` → reverts with `InvalidAmountToWithdraw`.
5. Alice calls `instantWithdrawal(ETH, 0.5e18, ...)`. The check at line 224 evaluates identically → reverts with `InvalidAmountToWithdraw`.
6. Alice's 0.5 rsETH (representing ~0.5 ETH of value) is frozen. She must acquire at least 0.5 more rsETH from the market and combine it to reach the 1 rsETH minimum before she can withdraw.

**Relevant code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L35-35)
```text
    mapping(address asset => uint256) public minRsEthAmountToWithdraw;
```

**File:** contracts/LRTWithdrawalManager.sol (L162-164)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L224-226)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L330-332)
```text
    function setMinRsEthAmountToWithdraw(address asset, uint256 minRsEthAmountToWithdraw_) external onlyLRTAdmin {
        minRsEthAmountToWithdraw[asset] = minRsEthAmountToWithdraw_;
        emit MinAmountToWithdrawUpdated(asset, minRsEthAmountToWithdraw_);
```
