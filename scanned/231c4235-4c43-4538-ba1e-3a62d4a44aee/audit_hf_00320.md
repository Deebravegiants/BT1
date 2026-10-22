# [M] `ConvexStakingWrapper#deposit

## Summary
Severity: Medium
Contest weight: 0.5897
Dataset id: 1573
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the value of `_amount` is larger than `type(uint192).max`, due to unsafe type casting, the recorded deposited amount can be much smaller than their invested amount.

[ConvexStakingWrapper.sol#L228-L250](https://github.com/code-423n4/2022-02-concur/blob/72b5216bfeaa7c52983060ebfc56e72e0aa8e3b0/contracts/ConvexStakingWrapper.sol#L228-L250)  

```solidity
function deposit(uint256 _pid, uint256 _amount)
    external
    whenNotPaused
    nonReentrant
{
    _checkpoint(_pid, msg.sender);
    deposits[_pid][msg.sender].epoch = currentEpoch();
    deposits[_pid][msg.sender].amount += uint192(_amount);
    if (_amount > 0) {
        IERC20 lpToken = IERC20(
            IRewardStaking(convexPool[_pid]).poolInfo(_pid).lptoken
        );

        lpToken.safeTransferFrom(msg.sender, address(this), _amount);
        lpToken.safeApprove(convexBooster, _amount);
        IConvexDeposits(convexBooster).deposit(_pid, _amount, true);
        lpToken.safeApprove(convexBooster, 0);
        uint256 pid = masterChef.pid(address(lpToken));
        masterChef.deposit(msg.sender, pid, _amount);
    }

    emit Deposited(msg.sender, _amount);
}
```

## Proof of Concept
When `_amount` = `uint256(type(uint192).max) + 1`:

* At L235, `uint192(_amount)` = `0`, `deposits[_pid][msg.sender].amount` = `0`;
* At L241, `uint256(type(uint192).max) + 1` will be transferFrom `msg.sender`.

Expected results:

`deposits[_pid][msg.sender].amount` == `uint256(type(uint192).max) + 1`;

Actual results:

`deposits[_pid][msg.sender].amount` = `0`.

The depositor loses all their invested funds.

## Recommendation
Consider adding a upper limit for the `_amount` parameter:
```solidity
require(_amount <= type(uint192).max, "...");
```
The warden has shown how casting without safe checks can cause the accounting to break and cause end users to lose deposited tokens.

While the finding has merit, I believe that because this applies to niche situations, and is conditional on specific inputs, that Medium Severity is more appropriate.
