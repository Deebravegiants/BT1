# [M] Potential Reentrancy Risk in Rewarder::onMntReward()

## Summary
Severity: Medium
Contest weight: 0.5942
Dataset id: 12499
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is effective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specifically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [9] exploit, and the recent Uniswap/Lendf.Me hack [8]. We notice there is an occasion where the checks-effects-interactions principle is violated. In the Rewarder contract, the onMntReward() function (see the code snippet below) is called from the MasterMantis to reward the staker with third-party's native token alongside MNT by externally calling a token contract to transfer rewards to the staker. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy. Apparently, the interaction with the external contract (lines 109, 111) starts before effecting the update on internal states (lines 115-116), hence violating the principle.
```solidity
function onMntReward(address _user, uint256 _lpAmount) external onlyMasterMantis {
    updatePool();
    PoolInfo memory pool = poolInfo;
    UserInfo storage user = userInfo[_user];
    uint256 pending;
    // if user had deposited
    if (user.amount > 0)
        pending = (user.amount * pool.accTokenPerShare / ACC_TOKEN_PRECISION) - user.rewardDebt;
    uint256 balance = rewardToken.balanceOf(address(this));
    if (pending > balance)
        rewardToken.safeTransfer(_user, balance);
    else
        rewardToken.safeTransfer(_user, pending);
    user.amount = _lpAmount;
    user.rewardDebt = user.amount * pool.accTokenPerShare / ACC_TOKEN_PRECISION;
    emit OnReward(_user, pending);
}
```
Because the onMntReward() function can only be called from the MasterMantis, which seems the issue is mitigated. However, our study shows that the MasterMantis itself is reentrant. In the following, we show the code snippet of the MasterMantis::withdrawFor() routine. It comes to our attention that this routine is not properly protected by the nonReentrant as in deposit()/withdraw(). As a result, the MasterMantis can be reentrant by calling any of the deposit()/withdraw() routines following the withdrawFor() routine.
```solidity
function withdrawFor(address recipient, uint256 _pid, uint256 _amount) external override onlyPoolContracts {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][recipient];
    ...
    if (address(rewarders[_pid]) != address(0))
        rewarders[_pid].onMntReward(recipient, user.amount);
    emit Withdraw(recipient, _pid, _amount);
}
```
Specifically, in the case when rewardToken is an ERC777 token, a bad actor could hijack a MasterMantis::withdrawFor() call before rewardToken.safeTransfer() in the onMntReward() routine with a callback function. Within the callback function, the bad actor could call the MasterMantis::withdraw() function which further calls the onMntReward(). Since the user.amount/user.rewardDebt are not updated yet, the bad actor can claim more rewards than it is expected. Public

## Recommendation
Apply the checks-effects-interactions design pattern in the Rewarder::onMntReward() routine or add the reentrancy guard modifier in the MasterMantis::withdrawFor() routine.
