# [M] Improper Withdrawal Logic In StakingLogic

## Summary
Severity: Medium
Contest weight: 0.4609
Dataset id: 12095
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The staking support allows the users to deposit the intended tokens into the staking contract. In the meantime, it also allows the user to redeem the staked funds. While examining the current unstaking logic, we notice the related logic also needs to be revisited. To elaborate, we show below the implementation of the related withdraw() routine. The current unstaking logic computes the withdraw fee and the sacrifice amount, next calculates the actual amount for withdrawal, i.e., tokensToWithdraw = tokenAmountOut - (wdFee - sac) (line 1312). Apparently, the current approach has an implicit assumption that wdFee >= sac, which unfortunately may not be the case. In the corner case where the sacrifice amount is larger than the withdraw fee, the current unstaking execution may be unexpectedly reverted! In addition, if the protocol parameter burnWDFee indicates the need of not burning the withdraw fee, the related fee is supposed to sent to the pool. However, it is not consistent with the current implementation, which simply keeps the fee in the withdrawing user account (lines 1315-1318).
```solidity
function withdraw(address user, uint256 amt) public pse returns(uint256 tokenAmountOut) {
    if(msg.sender != parent) {
        require(msg.sender == user, "Not user");
    }
    if(matureDelay) {
        require(block.timestamp >= stakers[user].stakeTime + delay, "Not mature");
    }
    if(DR(SD2(SD).DATA_READ()).feeConverter() != address(0)) {
        protCont(DR(SD2(SD).DATA_READ()).feeConverter()).cont(SD, 0);
    }
    if(userRewardCheck(user)) {
        claimAllReward(user);
        require(!userRewardCheck(user), "cl");
    }
    uint256 totalSD = IERC20(SD).balanceOf(parent);
    uint256 tokens = calcPoolInGivenSingleOut(
        totalSD,
        bmul(BASE, 25),
        _totalSupply,
        bmul(BASE, 25),
        amt
    );
    require(tokens <= balanceOf(user), "You don't have enough");
    tokenAmountOut = calcSingleOutGivenPoolIn(
        totalSD,
        bmul(BASE, 25),
        _totalSupply,
        bmul(BASE, 25),
        tokens
    );
    uint256 wdFee = tokenAmountOut.div(1000).mul(withdrawFee);
    if(burnWDFee) {
        stakeInterface(parent).sendTokens(dead, wdFee);
    }
    uint256 sac;
    if(sacrificeEnabled) {
        sac = tokenAmountOut.div(1000).mul(stakers[user].sacrificeLevel);
        stakeInterface(parent).sendTokens(dead, sac);
        tokenAmountOut = sac;
        emit USERSACRIFICE(user, sac);
    }
    uint256 tokensToWithdraw = tokenAmountOut - (wdFee - sac);
    _pullPoolShare(user, tokens);
    _burn(tokens);
    if(!burnWDFee && wdFee != 0) {
        amt = wdFee;
        stakers[user].amtStaked = amt;
        totalStakedSD = amt;
        if(balanceOf(user) == 0)
            stakers[user].amtStaked = 0;
        stakers[user].stakeTime = 0;
        stakers[user].initialized = false;
    }
    stakeInterface(parent).sendTokens(user, tokensToWithdraw);
    emit UNSTAKED(user, tokensToWithdraw);
    return tokensToWithdraw;
}
```

## Recommendation
Revise the above unstaking logic to avoid arithmetic underflow and return the fee to the current pool (if the protocol is configured to do so).
