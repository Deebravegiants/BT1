# [H] principle not updated in rebase() leading to underflow and withdrawal failures

## Summary
Severity: High
Contest weight: 0.7985
Dataset id: 14772
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The principle variable in the StakingToken contract is intended to track the
total amount of underlying tokens deposited into the contract. However, within
the rebase function, which adjusts the total supply of tokens (e.g., to reflect
accrued interest or rewards), the principle variable is not updated to match
the new total supply.
This mismatch leads to a critical issue: when the total supply increases due to a
rebase, but principle remains the same, subsequent calculations that rely on
principle can underflow. Specifically, during the unstaking process in the
_approveUnstakeRequest function, the contract attempts to subtract the
unstaked amount from principle. If the unstaked amount exceeds the
unchanged principle, this subtraction underflows, causing transactions to
fail.
As a result, users will be unable to withdraw their funds after a rebase that
increases the total supply, leading to a DoS, especially for the last withdrawing
users.
function test_rebase_doesnt_update_principle() public {
    uint256 amount = 1235038820;
    uint256 minStakingAmount = 1e6;
    uint16 stakingFeeBPS = 0;
    uint256 bridgingFee = 0;
    address rebaseAccount = makeAddr("Rebaser");
    address withdrawingAccount = makeAddr("Withdrawer");
    // Have the admin grant the WITHDRAWAL_ROLE and REBASE_ROLE to the accounts
    vm.startPrank(admin);
    stakingToken.grantRole(stakingToken.REBASE_ROLE(), rebaseAccount);
    stakingToken.grantRole(stakingToken.WITHDRAWAL_ROLE(), withdrawingAccount);
    vm.stopPrank();
    // Have the config manager set configs
    vm.startPrank(configManager);
    stakingToken.setMinStakingAmount(minStakingAmount);
    stakingToken.setStakingFeeBPS(stakingFeeBPS);
    stakingToken.setBridgingFee(bridgingFee);
    stakingToken.setProtocolVault(protocolVault);
    stakingToken.setMaxDepositPerRequest(type(uint256).max);
    stakingToken.setCap(type(uint256).max);
    vm.stopPrank();
    // Mint the amount of undelying tokens to userA
    mockUnderlyingToken.mint(userA, amount);
    // Have userA approve the staking token to pull the underlying token from them
    vm.prank(userA);
    mockUnderlyingToken.approve(address(stakingToken), amount);
    // Have userA deposit half the amount of underlying tokens
    vm.startPrank(userA);
    stakingToken.deposit(amount/2);
    vm.stopPrank();
    // Have the account call rebase with the new total supply +20%
    vm.startPrank(rebaseAccount);
    stakingToken.rebase(stakingToken.totalSupply() * 6/5);
    vm.stopPrank();
    // Have userA deposit the second half of underlying tokens
    vm.startPrank(userA);
    stakingToken.deposit(amount/2);
    vm.stopPrank();
    // Get the staking token balance of userA
    uint256 unstakingAmount = stakingToken.balanceOf(userA);
    // Mint the unstakingAmount of underlyingTokens to the withdrawingAccount and approve the staking token to pull them
    vm.startPrank(withdrawingAccount);
    mockUnderlyingToken.mint(withdrawingAccount, unstakingAmount);
    mockUnderlyingToken.approve(address(stakingToken), unstakingAmount);
    vm.stopPrank();
    vm.startPrank(userA);
    stakingToken.requestUnstake(unstakingAmount);
    vm.stopPrank();
    console.log("Asset Amount = %s", stakingToken.convertToAssets(request.shares));
    console.log("principle = %s", stakingToken.principle());
    // Have the withdrawingAccount approve the unstake request (Which will revert due to underflow)
    vm.startPrank(withdrawingAccount);
    vm.expectRevert(stdError.arithmeticError);
    stakingToken.approveUnstakeRequest();
    vm.stopPrank();
}
```

## Recommendation
Update the principle variable within the rebase function to accurately
reflect changes in the total supply. By synchronizing principle with the
adjusted total supply, you ensure that all calculations dependent on principle
remain accurate, preventing underflow errors and allowing users to withdraw
their funds without issues.
Specifically, consider adding logic to the rebase function similar to:
```solidity
function rebase(uint256 newTotalSupply) external onlyRole(REBASE_ROLE) {
    // Existing rebase logic...
    _updateApy(newTotalSupply, currentTotalSupply);
    lastRebaseTimestamp = block.timestamp;
    lastTotalSupply = currentTotalSupply;
    _rebase(newTotalSupply);
    // Update principle to match the new total supply
    principle = newTotalSupply;
}
```
This adjustment ensures that principle remains consistent with the total
supply after a rebase, maintaining the integrity of the contract's financial
calculations.
