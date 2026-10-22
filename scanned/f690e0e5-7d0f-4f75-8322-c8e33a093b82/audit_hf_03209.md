# [M] Staking#changeStakeTime and changeStakeAmount

## Summary
Severity: Medium
Contest weight: 0.4598
Dataset id: 17795
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Staking#changeStakeTime and changeStakeAmount allow the locking bonus to be modified. Any change to this value will cause voting imbalance in the system. If changes result in a higher total bonus then existing stakers will be given a permanent advantage over new stakers. If the bonus is increased then existing stakers will be at a disadvantage because they will be locked and unable to realize the new staking bonus.
```solidity
function _stakeToken(uint _tokenId, uint _unlockTime) internal returns (uint) {
    if (_unlockTime > 0) {
        unlockTime[_tokenId] = _unlockTime;
        uint fullStakedTimeBonus = ((_unlockTime - block.timestamp) * stakingSettings.maxStakeBonusAmount) / stakingSettings.maxStakeBonusTime;
        stakedTimeBonus[_tokenId] = _tokenId < 10000 ? fullStakedTimeBonus : fullStakedTimeBonus / 2;
    }
}
```
When a token is staked their stakeTimeBonus is stored. This means that any changes to stakingSettings.maxStakeBonusAmount or stakingSettings.maxStakeBonusTime won't affect tokens that are already stored. Storing the value is essential to prevent changes to the values causing major damage to the voting, but it leads to other more subtle issue when it is changed that will put either existing or new stakers at a disadvantage. Example: User A stake when maxStakeBonusAmount = 10 and stake long enough to get the entire bonus. Now maxStakeBonusAmount is changed to 20. User A is unable to unstake their token right away because it is locked. They are now at a disadvantage because other users can now stake and get a bonus of 20 while they are stuck with only a bonus of 10. Now maxStakeBonusAmount is changed to 5. User A now has an advantage because other users can now only stake for a bonus of 5. If User A never unstakes then they will forever have that advantage over new users. Voting power becomes skewed for users when Staking#changeStakeTime and changeStakeAmount are used.

## Recommendation
I recommend implementing a poke function that can be called by any user on any user. This function should loop through all tokens (or the tokens specified) and recalculate their voting power based on current multipliers, allowing all users to be normalized to prevent any abuse.
