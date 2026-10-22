# [M] Potential Reentrancy Risk in AvaxPool::deposit()/withdraw()

## Summary
Severity: Medium
Contest weight: 0.4594
Dataset id: 12280
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is effective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specifically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [16] exploit, and the recent Uniswap/Lendf.Me hack [15]. In the AvaxPool contract, we notice both of the deposit() and withdraw() functions have potential reentrancy risk. In the following, we use the deposit() routine as an example. To elaborate, we show below the code snippet of the deposit() routine in AvaxPool. In the depositHrnAndToken() function, we notice IERC20(multLpToken).safeTransfer(_user, tokenPending) (line 325) will be called to transfer the accumulated rewards to the user before depositing new underlying assets into the AvaxPool and pool.lpToken.safeTransferFrom(_user, address(this), _amount) (line 329) will be called to transfer the underlying assets into the AvaxPool. If the multLpToken or pool.lpToken faithfully implements the ERC777-like standard, then the deposit() routine is vulnerable to reentrancy and this risk needs to be properly mitigated. Specifically, the ERC777 standard normalizes the ways to interact with a token contract while remaining backward compatible with ERC20. Among various features, it supports send/receive hooks to offer token holders more control over their tokens. Specifically, when transfer() or transferFrom() actions happen, the owner can be notified to make a judgment call so that she can control (or even reject) which token they send or receive by correspondingly registering tokensToSend() and tokensReceived() hooks. Consequently, any transfer() or transferFrom() of ERC777-based tokens might introduce the chance for reentrancy or hook execution for unintended purposes (e.g., mining GasTokens). In our case, the above hook can be planted in IERC20(multLpToken).safeTransfer(_user, tokenPending) (line 325) or pool.lpToken.safeTransferFrom(_user, address(this), _amount) (line 329) before the actual transfer of the underlying assets occurs. By doing so, we can effectively keep user.rewardDebt and user.multLpRewardDebt intact (used for the calculation of pending rewards at line 315 and line 323). With a lower user.rewardDebt and user.multLpRewardDebt, the re-entered deposit() is able to obtain more rewards. It can be repeated to exploit this vulnerability for gains, just like earlier Uniswap/imBTC hack [15].

```solidity
/**
 * Deposit LP tokens AvaxPool for HRN allocation.
 */
function deposit(uint256 _pid, uint256 _amount) public notPause {
    PoolInfo storage pool = poolInfo[_pid];
    if (isMultLP(address(pool.lpToken))) {
        depositHrnAndToken(_pid, _amount, msg.sender);
    } else {
        depositHrn(_pid, _amount, msg.sender);
    }
}

function depositHrnAndToken(uint256 _pid, uint256 _amount, address _user) private {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][_user];
    updatePool(_pid);
    if (user.amount > 0) {
        uint256 pendingAmount = user.amount.mul(pool.accHrnPerShare).div(1e12).sub(user.rewardDebt);
        if (pendingAmount > 0) {
            safeHrnTransfer(_user, pendingAmount);
        }
        uint256 beforeToken = IERC20(multLpToken).balanceOf(address(this));
        IMasterChefAvax(multLpChef).deposit(poolCorrespond[_pid], 0);
        uint256 afterToken = IERC20(multLpToken).balanceOf(address(this));
        pool.accMultLpPerShare = pool.accMultLpPerShare.add(afterToken.sub(beforeToken).mul(1e12).div(pool.totalAmount));
        uint256 tokenPending = user.amount.mul(pool.accMultLpPerShare).div(1e12).sub(user.multLpRewardDebt);
        if (tokenPending > 0) {
            IERC20(multLpToken).safeTransfer(_user, tokenPending);
        }
    }
    if (_amount > 0) {
        pool.lpToken.safeTransferFrom(_user, address(this), _amount);
        if (pool.totalAmount == 0) {
            IMasterChefAvax(multLpChef).deposit(poolCorrespond[_pid], _amount);
        } else {
            uint256 beforeToken = IERC20(multLpToken).balanceOf(address(this));
            IMasterChefAvax(multLpChef).deposit(poolCorrespond[_pid], _amount);
            uint256 afterToken = IERC20(multLpToken).balanceOf(address(this));
            pool.accMultLpPerShare = pool.accMultLpPerShare.add(afterToken.sub(beforeToken).mul(1e12).div(pool.totalAmount));
        }
    }
    user.amount = user.amount.add(_amount);
    pool.totalAmount = pool.totalAmount.add(_amount);
    user.rewardDebt = user.amount.mul(pool.accHrnPerShare).div(1e12);
    user.multLpRewardDebt = user.amount.mul(pool.accMultLpPerShare).div(1e12);
    emit Deposit(_user, _pid, _amount);
}
```
Note the withdraw() routine in the same contract shares the same issue.

## Recommendation
Add necessary reentrancy guards to prevent unwanted reentrancy risks.
