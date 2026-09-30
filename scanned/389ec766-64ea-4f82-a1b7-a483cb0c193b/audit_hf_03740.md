# [H] Adversary can permanently break reward dis-

## Summary
Severity: High
Contest weight: 0.3398
Dataset id: 19877
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When closeCompetition is called for TieredPercentageBountyV1 it takes a snapshot of the current token balance. Afterwards it uses this number to calculate the payouts. When a deposit is refunded after the competition is closed then the contract won't have enough funds to pay users.
To exploit this an adversary can make a deposit for a token that has a current balance of zero using a expiration of 1 second. After the competition closes they refund their deposit. Now when the contract tries to give payouts to the winners it will try to payout a token that it no longer has any of, causing it to revert anytime someone tries to claim a payout.
plementations/TieredPercentageBountyV1.sol#L123-L136
token.
plementations/TieredPercentageBountyV1.sol#L104-L120
For each token in tokenAddresses it will send the claimedBalance to the claimant. If a deposit is refunded after the competition is closed then the contract won't have enough funds to pay users.
An adversary can exploit this by making a deposit of 100 for some token with and _expiration of 1 (second). After the competition has been closed they can refund their deposit causing the contract to be short on funds. If the user makes a deposit with an ERC20 token payouts can be re-enabled by donating to make the contract whole. The user can permanently break payouts by using native MATIC as the deposit. All bounty contracts have their receive function disabled which means the contract can't just be funded, which permanently breaks payouts.
Submitting as high because it can be combined with methods for breaking refunds to lock user funds permanently.
Adversary can permanently break TieredPercentageBounty payouts

## Recommendation
Since TieredPercentageBounty is designed to distribute all deposits present at closing, refunds should be disabled after the competition is closed.
