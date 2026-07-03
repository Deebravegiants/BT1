The code confirms the finding exactly. Both `initiateWithdrawal` at line 162 and `instantWithdrawal` at line 224 apply the same unconditional check with no bypass for full-balance withdrawals. The `minRsEthAmountToWithdraw` mapping is admin-configurable with no upper bound constraint. There is no alternative withdrawal path in the contract. The SECURITY.md does not exclude this class of issue.

Audit Report

## Title
Unconditional Minimum rsETH Check Traps Sub-Threshold Balances With No Withdrawal Path - (File: contracts/LRTWithdrawalManager.sol)

## Summary
`LRTWithdrawalManager` enforces a per-asset minimum rsETH amount in both `initiateWithdrawal` and `instantWithdrawal` with no exception for a user withdrawing their entire remaining balance. Any user who makes a partial withdrawal that leaves a remainder below `minRsEthAmountToWithdraw[asset]` has no on-chain path to redeem that remainder, temporarily freezing those funds until the user acquires additional rsETH from the open market.

## Finding Description
`minRsEthAmountToWithdraw[asset]` is stored as a per-asset mapping and set by the admin via `setMinRsEthAmountToWithdraw` with no upper bound. [1](#0-0) [2](#0-1) 

Both withdrawal entry points apply the check unconditionally:

`initiateWithdrawal`: [3](#0-2) 

`instantWithdrawal`: [4](#0-3) 

Neither check tests whether `rsETHUnstaked` equals the caller's full rsETH balance. There is no third withdrawal function in the contract. A user who performs a partial withdrawal that leaves a sub-threshold remainder has no recourse within the contract.

## Impact Explanation
**Medium — Temporary freezing of funds.** The user's rsETH tokens represent a proportional claim on protocol-held ETH/LST assets. When the remaining balance falls below the configured minimum, those tokens cannot be redeemed through any on-chain path. The funds are frozen until the user purchases additional rsETH on the open market to exceed the threshold, incurring direct financial cost. This matches the allowed impact class "Medium. Temporary freezing of funds."

## Likelihood Explanation
**Medium.** The scenario requires only a normal partial withdrawal — no special permissions, no front-running, no external protocol failure. The minimum is admin-configurable to any value and is expected to be non-zero in production. Any user who does not withdraw their entire balance in a single transaction is at risk. The condition is repeatable and affects all supported assets.

## Recommendation
Add a full-balance bypass to the minimum check in both `initiateWithdrawal` and `instantWithdrawal`:

```solidity
uint256 userBalance = IERC20(lrtConfig.rsETH()).balanceOf(msg.sender);
if (rsETHUnstaked == 0 ||
    (rsETHUnstaked < minRsEthAmountToWithdraw[asset] && rsETHUnstaked != userBalance)) {
    revert InvalidAmountToWithdraw();
}
```

This allows users to drain their entire remaining balance even when it is below the configured minimum, while still preventing dust withdrawals in the normal case.

## Proof of Concept
1. Admin calls `setMinRsEthAmountToWithdraw(ETH, 1e18)` — minimum is 1 rsETH.
2. Alice deposits 2 ETH via `LRTDepositPool.depositETH`, receiving 2 rsETH.
3. Alice calls `initiateWithdrawal(ETH, 1.5e18, "")`. Check: `1.5e18 >= 1e18` → passes. Alice now holds 0.5 rsETH.
4. Alice calls `initiateWithdrawal(ETH, 0.5e18, "")`. Check at line 162: `0.5e18 < 1e18` → reverts `InvalidAmountToWithdraw`.
5. Alice calls `instantWithdrawal(ETH, 0.5e18, "")`. Check at line 224: identical → reverts `InvalidAmountToWithdraw`.
6. Alice's 0.5 rsETH (~0.5 ETH of value) is frozen. She must buy ≥0.5 rsETH on the open market and retry.

**Foundry test sketch:**
```solidity
function test_dustTrap() public {
    vm.prank(admin);
    withdrawalManager.setMinRsEthAmountToWithdraw(ETH, 1e18);

    vm.startPrank(alice);
    depositPool.depositETH{value: 2e18}("");
    withdrawalManager.initiateWithdrawal(ETH, 1.5e18, ""); // succeeds
    vm.expectRevert(ILRTWithdrawalManager.InvalidAmountToWithdraw.selector);
    withdrawalManager.initiateWithdrawal(ETH, 0.5e18, ""); // reverts
    vm.stopPrank();
}
```

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
