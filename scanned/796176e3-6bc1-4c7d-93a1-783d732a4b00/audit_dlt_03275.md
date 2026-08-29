# [M] Consistently check account balance before and after transfers for Fee-On-Transfer discrepancies

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-vetoken
Published: 2022-06-02
Source: https://github.com/code-423n4/2022-05-vetoken-findings/issues/190
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-vetoken/blob/2d7cd1f6780a9bcc8387dea8fecfbd758462c152/contracts/Booster.sol#L356
https://github.com/code-423n4/2022-05-vetoken/blob/2d7cd1f6780a9bcc8387dea8fecfbd758462c152/contracts/VE3DRewardPool.sol#L337


# Vulnerability details

As arbitrary ERC20 tokens can be passed, the amount here should be calculated every time to take into consideration a possible fee-on-transfer or deflation.
Also, it's a good practice for the future of the solution.

Affected code:

- File: Booster.sol

```solidity
345:     function deposit(
346:         uint256 _pid,
347:         uint256 _amount,
348:         bool _stake
349:     ) public returns (bool) {
...
356:         IERC20(lptoken).safeTransferFrom(msg.sender, staker, _amount); //@audit medium: not compatible with Fee On Transfer Tokens
...
372:             ITokenMinter(token).mint(address(this), _amount);
...
374:             IERC20(token).safeApprove(rewardContract, _amount);
375:             IRewards(rewardContract).stakeFor(msg.sender, _amount);
...
378:             ITokenMinter(token).mint(msg.sender, _amount);
...
381:         emit Deposited(msg.sender, _pid, _amount);
...
```

- File: VE3DRewardPool.sol

```solidity
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-05-vetoken-findings/issues/190_
