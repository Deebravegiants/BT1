# [M] Potential Failed withdraw() After Transferring LP Token

## Summary
Severity: Medium
Contest weight: 0.4593
Dataset id: 11751
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BSCSBaseStartPool contract allows users to stake the underlying stakedToken token and get in return LP token (i.e., "BSCS BSCS Start Pool") to represent the pool shares. Meanwhile, the BSCSBaseStartPool contract supports all the standard ERC20 interfaces (including transfer()/transferFrom()) since it inherits from the standard ERC20 contract. In other words, the LP token can be transferred like the standard ERC20 token. While examining the logics of the deposit()/withdraw() routines, we notice there is a potential vulnerability that may result in the failure of the call to withdraw(). To elaborate, we show below the related code snippet of the BSCSBaseStartPool contract. In the deposit() function, the following statement is executed to record the user's deposit amount: user.amount = user.amount.add(_amount) (line 1134), and at the same time the same amount of LP token will be minted (line 1140). In the withdraw() function, the user.amount will be subtracted from the withdrawable amount of the underlying token (line 1190), and the same withdraw amount of LP token will be burned (line 1191). This is reasonable under the assumption that the vault's internal asset balances (i.e., user.amount) are always consistent with actual token balances maintained in individual ERC20 token contracts. However, we notice the transfer() interface of the BSCSBaseStartPool contract is inherited from the standard ERC20 contract, which only maintains the LP token balances. If we assume Alice transfers the LP token to Bob, both Alice and Bob cannot withdraw the deposit underlying token because of the inconsistency between the internal asset records (i.e., user.amount) and LP token balances maintained in ERC20 token contracts. We suggest to override the _transfer() interface to add the internal asset balances (i.e., user.amount) update.
```solidity
function deposit(uint256 _amount) external nonReentrant {
    UserInfo storage user = userInfo[msg.sender];
    require(stakingBlock <= block.number, "Staking has not started");
    require(stakingEndBlock >= block.number, "Staking has ended");
    if (hasPoolLimit) {
        uint256 stakedTokenSupply = stakedToken.balanceOf(address(this));
        require(
            _amount.add(stakedTokenSupply) <= poolCap,
            "Pool cap reached"
        );
    }
    if (hasUserLimit) {
        require(
            _amount.add(user.amount) <= poolLimitPerUser,
            "User amount above limit"
        );
    }
    _updatePool();
    if (user.amount > 0) {
        uint256 pending;
        for (uint256 i = 0; i < rewardTokens.length; i++) {
            pending = user.amount.mul(accTokenPerShare[rewardTokens[i]]).div(PRECISION_FACTOR[rewardTokens[i]]).sub(user.rewardDebt[rewardTokens[i]]);
            if (pending > 0) {
                ERC20(rewardTokens[i]).transfer(address(msg.sender), pending);
            }
        }
    }
    if (_amount > 0) {
        user.amount = user.amount.add(_amount);
        ERC20(stakedToken).transferFrom(address(msg.sender), address(this), _amount);
        _mint(address(msg.sender), _amount);
    }
    for (uint256 i = 0; i < rewardTokens.length; i++) {
        user.rewardDebt[rewardTokens[i]] = user.amount.mul(accTokenPerShare[rewardTokens[i]]).div(PRECISION_FACTOR[rewardTokens[i]]);
    }
    user.lastStakingBlock = block.number;
    emit Deposit(msg.sender, _amount);
}

function withdraw(uint256 _amount) external nonReentrant {
    UserInfo storage user = userInfo[msg.sender];
    require(unStakingBlock <= block.number, "Unstaking has not started");
    require(user.amount >= _amount, "Amount to withdraw too high");
    _updatePool();
    uint256 pending = user.amount.mul(accTokenPerShare).div(PRECISION_FACTOR).sub(user.rewardDebt);
    uint256 pending;
    for (uint256 i = 0; i < rewardTokens.length; i++) {
        pending = user.amount.mul(accTokenPerShare[rewardTokens[i]]).div(PRECISION_FACTOR[rewardTokens[i]]).sub(user.rewardDebt[rewardTokens[i]]);
        if (pending > 0) {
            // ERC20( rewardTokens [i]).transfer(address(msg.sender), pending);
            safeERC20Transfer(ERC20(rewardTokens[i]), address(msg.sender), pending);
        }
    }
    if (_amount > 0) {
        user.amount = user.amount.sub(_amount);
        _burn(address(msg.sender), _amount);
        _amount = collectFee(_amount, user);
        ERC20(stakedToken).transfer(address(msg.sender), _amount);
        // _burn(address(msg.sender),_amount);
    }
    for (uint256 i = 0; i < rewardTokens.length; i++) {
        user.rewardDebt[rewardTokens[i]] = user.amount.mul(accTokenPerShare[rewardTokens[i]]).div(PRECISION_FACTOR[rewardTokens[i]]);
    }
    emit Withdraw(msg.sender, _amount);
}
```
Moreover, we notice there is a lack of the reward recalculation during transferring the LP token, which will introduce unexpected loss. Given this, we suggest to override the _transfer() interface in the BSCSBaseStartPool contract to add the reward recalculation mechanism.

## Recommendation
Suggest to override the _transfer() interface as above-mentioned.
