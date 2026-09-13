# [C] 5.1.1 Rewardcalculatesearnedincorrectly on each epoch boundary

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** Reward.sol#L161-L
**Description:** Rewards are allocated on a per epoch basis to users in proportion to their total deposited amount.
Because the balance and total supply used for rewards is based on_currTs % WEEK + WEEK, the values will not
represent the end of the current epoch, but instead the first second of the next epoch.
As a result, if a user deposits at any epoch boundary, their deposited amount will actually contribute to the check-
pointed total supply of the prior epoch. This leads to a few issues which are detailed below:

- Users who deposit in the first second of the next epoch will dilute the total supply for the prior epoch while
    not being eligible to claim rewards for that same epoch. Consequently, some rewards will be left unclaimed
    and locked within the contract as thetokenRewardsPerEpochmapping is used to store reward amounts so
    unclaimed rewards will not roll over to future epochs.
- Users can also avoid zeronumEpochsby depositing a negligible amount at an earlier epoch for multiple ac-
    counts before attempting to deposit a larger amount at_currTs % WEEK == 0. The same user can withdraw
    their deposit from theVotingEscrowcontract with the claimed rewards and re-deposit these funds into an-
    other account in the same block. They are able to abuse this issue to claim all rewards allocated to each
    epoch.
- In a similar fashion, reward distributions that are weighted by users' votes in theVotercontract can suffer the
    same issue as outlined above. If the attacker votes some negligible amount on various pools using several
    accounts, they can increase the vote, claim, reset the vote and re-vote via another account to claim rewards
    multiple times.
The math below shows that_currTs + WEEKis indeed the first second of the next epoch and not the last of the
prior epoch.


```
uint256 internal constant WEEK = 7 days;
function epochStart(uint256 timestamp) internal pure returns (uint256) {
return timestamp - (timestamp % WEEK);
}
epochStart(123)
Type: uint
Hex: 0x
Decimal: 0
epochStart(100000000)
Type: uint
Hex: 0x5f2b
Decimal: 99792000
WEEK
Type: uint
Hex: 0x93a
Decimal: 604800
epochStart(WEEK)
Type: uint
Hex: 0x93a
Decimal: 604800
epochStart(1 + WEEK)
Type: uint
Hex: 0x93a
Decimal: 604800
epochStart(0 + WEEK)
Type: uint
Hex: 0x93a
Decimal: 604800
epochStart(WEEK - 1)
Type: uint
Hex: 0x
Decimal: 0
```
**Recommendation:** Both lines which query the user's prior balance and total supply for each given epoch can be
replaced to check only the last second of the epoch:
if (numEpochs > 0) {
for (uint256 i = 0; i < numEpochs; i++) {
// get index of last checkpoint in this epoch
+ _index = getPriorBalanceIndex(tokenId, _currTs + DURATION - 1);

- _index = getPriorBalanceIndex(tokenId, _currTs + DURATION);
    // get checkpoint in this epoch
    cp0 = checkpoints[tokenId][_index];
    // get supply of last checkpoint in this epoch
+ _supply = Math.max(supplyCheckpoints[getPriorSupplyIndex(_currTs + DURATION - 1)].supply, 1);
- _supply = Math.max(supplyCheckpoints[getPriorSupplyIndex(_currTs + DURATION)].supply, 1);
    reward += (cp0.balanceOf * tokenRewardsPerEpoch[token][_currTs]) / _supply;
    _currTs += DURATION;
}
}

This will ensure that users who deposit at the start of the following epoch will not be eligible for rewards or dilute
the supply whenblock.timestamp % WEEK == 0.
**Velodrome:** Fixed in commit 02e0bc.
**Spearbit:** Verified.
