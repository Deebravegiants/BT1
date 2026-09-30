# [M] Admin can lock funds

## Summary
Severity: Medium
Contest weight: 0.4764
Dataset id: 5243
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While there are checks that the owner (admin/reward notifier) doesn't misbehave by setting a reward token to 0 or setting the duration to 0, there are no checks that the owner doesn't use the fatBERA tokens as reward tokens. If they do, these tokens would be lost to the system (see the proof of concept). It would be best to check that the reward token is not address(0) and not address(this) in the notifyRewardAmount function.

## Proof of Concept
```solidity
function test_notifyRewardAmountVaultTokens() public {
    // Alice deposits after failed reward
    vm.prank(alice);
    vault.deposit(10e18, alice);
    // Verify no rewards from before deposit
    assertEq(vault.previewRewards(alice, address(wbera)), 0, "Should have no rewards from before deposit");
    // New reward should work
    vm.startPrank(admin);
    vault.deposit(10e18, admin);
    vault.setRewardsDuration(address(vault), 7 days);
    vault.approve(address(vault), type(uint256).max);
    vm.stopPrank();
    notifyAndWarp(address(vault), 10e18);
    assertApproxEqAbs(vault.previewRewards(alice, address(vault)), 5e18, tolerance, "Should receive new rewards");
    assertApproxEqAbs(vault.previewRewards(admin, address(vault)), 0, tolerance, "Admin should receive new rewards");
    assertEq(vault.balanceOf(admin), 0e18, "Admin should have deposited all 10e18");
    // Record balance before claim
    uint256 balanceBefore = vault.balanceOf(alice);
    // Claim rewards
    vm.prank(alice);
    vault.claimRewards(address(alice));
    // Verify reward received
    assertApproxEqAbs(vault.balanceOf(alice) - balanceBefore, 5e18, tolerance, "Should receive full reward");
    assertEq(vault.previewRewards(alice, address(vault)), 0, "Rewards should be zero after claim");
}
```

## Recommendation
No data
