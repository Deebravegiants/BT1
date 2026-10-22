# [H] Adversary can permanently brick auctions due

## Summary
Severity: High
Contest weight: 0.7867
Dataset id: 20334
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When batch depositing to ProtocolRewards, the msg.value is expected to match the sum of the amounts array EXACTLY. The issue is that due to precision loss in Auction#_computeTotalRewards this call can be engineered to always revert which completely bricks the auction process.
ProtocolRewards.sol#L55-L65
```solidity
for (uint256 i; i < numRecipients; ) {
    expectedTotalValue += amounts[i];
    unchecked {
        ++i;
    }
}
if (msg.value != expectedTotalValue) {
    revert INVALID_DEPOSIT();
}
```
When making a batch deposit the above method is called. As seen, the call will revert if the sum of amounts does not EXACTLY equal the msg.value. Auction.sol#L474-L507
```solidity
uint256 totalBPS = _founderRewardBps + referralRewardsBPS + builderRewardsBPS;
// Calulate total rewards
split.totalRewards = (_finalBidAmount * totalBPS) / BPS_PER_100_PERCENT;
// Initialize arrays
split.recipients = new address[](arraySize);
split.amounts = new uint256[](arraySize);
split.reasons = new bytes4[](arraySize);
// Set builder reward
split.recipients[0] = builderRecipient;
split.amounts[0] = (_finalBidAmount * builderRewardsBPS) / BPS_PER_100_PERCENT;
// Set referral reward
split.recipients[1] = _currentBidRefferal != address(0) ? _currentBidRefferal : builderRecipient;
split.amounts[1] = (_finalBidAmount * referralRewardsBPS) / BPS_PER_100_PERCENT;
// Set founder reward if enabled
if (hasFounderReward) {
    split.recipients[2] = founderReward.recipient;
    split.amounts[2] = (_finalBidAmount * _founderRewardBps) / BPS_PER_100_PERCENT;
}
```
The sum of the percentages are used to determine the totalRewards. Meanwhile, the amounts are determined using the broken out percentages of each. This leads to unequal precision loss, which can cause totalRewards to be off by a single wei which cause the batch deposit to revert and the auction to be bricked. Take the following example: Assume a referral reward of 5% (500) and a builder reward of 5% (500) for a total of 10% (1000). To brick the contract the adversary can engineer their bid with specific split.totalRewards = (19 * 1,000) / 100,000 = 190,000 / 100,000 = 1 split.amounts[0] = (19 * 500) / 100,000 = 95,000 / 100,000 = 0 split.amounts[1] = (19 * 500) / 100,000 = 95,000 / 100,000 = 0 Here we can see that the sum of amounts is not equal to totalRewards and the batch deposit will revert.
Auction.sol#L270-L273
```solidity
if (split.totalRewards != 0) {
    // Deposit rewards
    rewardsManager.depositBatch{ value: split.totalRewards }(split.recipients, split.amounts, split.reasons, "");
}
```
The depositBatch call is placed in the very important _settleAuction function. This results in auctions that are permanently broken and can never be settled. Auctions are completely bricked

## Recommendation
Instead of setting totalRewards with the sum of the percentages, increment it by each fee calculated. This way they will always match no matter what.
