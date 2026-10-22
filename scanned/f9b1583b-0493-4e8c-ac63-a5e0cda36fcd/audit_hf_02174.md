# [M] Proper Logic in LockRewards::withdrawLocked()

## Summary
Severity: Medium
Contest weight: 0.4602
Dataset id: 12127
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The GoldRoom protocol has a built-in staking subsystem to incentivize staking users. If the user chooses a lockup period, the user will receive a boosted reward that is calculated from the chosen lockup period. While examining the boosted logic for staking and unstaking, we notice the logic needs to be improved. Speciﬁcally, the issue stems from the lack of boosted amount calculation when the staked assets are removed. To elaborate, we show below the related withdrawLocked() function. As the name indicates, this function is designed to withdraw locked funds that were staked before. And the withdraw logic needs to properly reduct the withdrawn amount from the recorded staking token balance and boosted balance. However, the reduction from the boosted balance (line 187) fails to take into consideration of lockup period. Moreover, it decreases the boosted supply with the wrong amount (line 191) and burns the wrong number of veTokens (line 200).
```solidity
function withdrawLocked(bytes32 kek_id) external override nonReentrant {
    LockedStake memory thisStake;
    thisStake.amount = 0;
    uint theIndex;
    for (uint i = 0; i < lockedStakes[msg.sender].length; i++){
        if (kek_id == lockedStakes[msg.sender][i].kek_id){
            thisStake = lockedStakes[msg.sender][i];
            theIndex = i;
            break;
        }
    }
    require(thisStake.kek_id == kek_id, "Stake not found");
    require(block.timestamp >= thisStake.ending_timestamp || unlockedStakes == true, "Stake is still locked!");
    uint256 theAmount = thisStake.amount;
    if (theAmount > 0){
        // Staking token balance and boosted balance
        _locked_balances[msg.sender] = _locked_balances[msg.sender].sub(theAmount);
        _boosted_balances[msg.sender] = _boosted_balances[msg.sender].sub(theAmount);
        // Staking token supply and boosted supply
        _staking_token_supply = _staking_token_supply.sub(theAmount);
        _staking_token_boosted_supply = _staking_token_boosted_supply.sub(theAmount);
        // Remove the stake from the array
        delete lockedStakes[msg.sender][theIndex];
        // Give the tokens to the withdrawer
        stakingToken.safeTransfer(msg.sender, theAmount);
        // burn the veToken corresponding to Token
        VEToken(veToken).burn(msg.sender, theAmount);
        emit WithdrawnLocked(msg.sender, theAmount, kek_id);
    }
}
```

## Recommendation
Properly calculate the boosted amount for reduction when the locked assets are being unstaked and withdrawn.
