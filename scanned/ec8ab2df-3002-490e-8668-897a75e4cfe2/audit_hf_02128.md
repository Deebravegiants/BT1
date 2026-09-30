# [M] Suggested Adherence of Checks-Effects-Interaction Pattern

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 11946
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle.
This principle is effective in mitigating a serious attack vector known as re-entrancy.
Via this
particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested
manner. Specifically, it first calls a function in the vulnerable contract, but before the first instance
of the function call is finished, second call can be arranged to re-enter the vulnerable contract by
invoking functions that should only be executed once. This attack was part of several most prominent
hacks in Ethereum history, including the DAO [18] exploit, and the recent Uniswap/Lendf.Me hack [17].
We notice there is an occasion where the checks-effects-interactions principle is violated. Using
the SinglePool contract as an example, the emergencyWithdraw() function (see the code snippet below)
is provided to externally call a token contract to transfer assets. However, the invocation of an external
contract requires extra care in avoiding the above re-entrancy.
Apparently, the interaction with the external contract (line 204) starts before effecting the update
on internal states (lines 210-211), hence violating the principle. In this particular case, if the external
Public
contract has certain hidden logic that may be capable of launching re-entrancy via the same entry
function.
```solidity
// Withdraw without caring about rewards. EMERGENCY ONLY.
function emergencyWithdraw() public {
    PoolInfo storage pool = poolInfo[0];
    UserInfo storage user = userInfo[msg.sender];
    pool.lpToken.safeTransfer(address(msg.sender), user.amount);
    if (totalDeposit >= user.amount) {
        totalDeposit = totalDeposit.sub(user.amount);
    } else {
        totalDeposit = 0;
    }
    user.amount = 0;
    user.rewardDebt = 0;
    emit EmergencyWithdraw(msg.sender, user.amount);
}
```
Note that other routines SinglePool::deposit() and SinglePool::withdraw() share the same issue.

## Recommendation
Apply necessary reentrancy prevention by utilizing the nonReentrant modifier
to block possible re-entrancy.
