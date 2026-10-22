# [H] pUSDeVault::maxWithdraw doesn't account for withdrawal pausing, in violation of EIP-4626

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23529
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
pUSDeVault::maxWithdraw doesn't account for withdrawal pausing, in violation of EIP-4626 which can break protocols integrating with pUSDeVault.  
EIP-4626 states on maxWithdraw:  
MUST factor in both global and user-specific limits, like if withdrawals are entirely disabled (even temporarily) it MUST return 0.

## Proof of Concept
```solidity
function test_maxWithdraw_WhenWithdrawalsPaused() external {
    // user1 deposits $1000 USDe into the main vault
    uint256 user1AmountInMainVault = 1000e18;
    USDe.mint(user1, user1AmountInMainVault);
    vm.startPrank(user1);
    USDe.approve(address(pUSDe), user1AmountInMainVault);
    uint256 user1MainVaultShares = pUSDe.deposit(user1AmountInMainVault, user1);
    vm.stopPrank();
    // admin pauses withdrawals
    pUSDe.setWithdrawalsEnabled(false);
    // reverts as maxWithdraw returns user1AmountInMainVault even though
    // attempting to withdraw would revert
    assertEq(pUSDe.maxWithdraw(user1), 0);
    // https://eips.ethereum.org/EIPS/eip-4626 maxWithdraw says:
    // MUST factor in both global and user-specific limits,
    // like if withdrawals are entirely disabled (even temporarily) it MUST return 0
}
```

## Recommendation
When withdrawals are paused, maxWithdraw should return 0. The override of maxWithdraw should likely be done in PreDepositVault because there is where the pausing is implemented.
