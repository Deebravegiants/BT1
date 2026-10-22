# [M] Potential Reentrancy in withdraw()

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 11848
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is effective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specifically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [16] exploit, and the recent Uniswap/Lendf.Me hack [15]. We notice there is an occasion where the checks-effects-interactions principle is violated. Using the SkyRewardPool as an example, the withdraw() function (see the code snippet below) is provided to withdraw LP tokens from the pool. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy. Apparently, the interaction with the external contract (lines 224 and 229) starts before effecting the update on internal states (line 231), hence violating the principle. In this particular case, if the external contract has certain hidden logic that may be capable of launching re-entrancy via the same entry function.
```solidity
function withdraw(uint256 _pid, uint256 _amount) public {
    address _sender = msg.sender;
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][_sender];
    require(user.amount >= _amount, "withdraw: not good");
    updatePool(_pid);
    uint256 _pending = user.amount.mul(pool.accSkyPerShare).div(1e18).sub(user.rewardDebt);
    if (_pending > 0) {
        safeSkyTransfer(_sender, _pending);
        emit RewardPaid(_sender, _pending);
    }
    if (_amount > 0) {
        user.amount = user.amount.sub(_amount);
        pool.token.safeTransfer(_sender, _amount);
        user.rewardDebt = user.amount.mul(pool.accSkyPerShare).div(1e18);
        emit Withdraw(_sender, _pid, _amount);
    }
}
```
Note another routine deposit() shares the same issue.

## Recommendation
Apply necessary reentrancy prevention by utilizing the nonReentrant modifier to block possible re-entrancy.
