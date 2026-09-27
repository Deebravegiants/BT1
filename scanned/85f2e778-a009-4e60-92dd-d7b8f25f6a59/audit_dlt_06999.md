# [M] Rewards can be lost

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-redacted-cartel
Published: 2022-02-15
Source: https://github.com/code-423n4/2022-02-redacted-cartel-findings/issues/13
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/RewardDistributor.sol#L97


# Vulnerability details

## Impact
Reward can be lost if bribeVault calls the updateRewardsMetadata on same rewardIdentifier again before user can claim his reward (since merkleRoot and proof will get updated)

## Proof of Concept
1. bribeVault calls the updateRewardsMetadata at RewardDistributor.sol#L97 using rewardIdentifier X
2. Assume  _distributions[i].proof contains merkle proof for User A
3. User A fails to call claim function
4. bribeVault again calls the updateRewardsMetadata at RewardDistributor.sol#L97 using rewardIdentifier X updating  _distributions[i].proof  which might not contain merkle proof of User A now. So User A loses his rewards

## Recommended Mitigation Steps
bribeVault should only make second call to updateRewardsMetadata on same rewardIdentifier when all claimers have made there claims
