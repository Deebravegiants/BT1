# [H] Adversary can permanently break percent-

## Summary
Severity: High
Contest weight: 0.2949
Dataset id: 19876
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some ERC20 tokens don't support 0 value transfers. An adversary can abuse this by adding it to a percentage tier bounty then refunding it. This is because after the refund the token will still be on the list of tokens to distribute but it will have a value saved of 0. This means that no matter what it will always try to transfer 0 token and this will always revert because the specified token doesn't support zero transfers.
plementations/TieredPercentageBountyV1.sol#L123-L136
token. If a token has no balance then the fundingTotals for that token will be zero.
plementations/TieredPercentageBountyV1.sol#L104-L120
For each token in tokenAddresses it will send the claimedBalance to the claimant. If fundingTotal is 0 then it will attempt to call transfer with an amount of 0. Some ERC20 tokens will revert on transfers like this.
An adversary can purposefully trigger these conditions by making a deposit with ERC20 token that has this problem. This will add the ERC20 token to tokenAddresses and cause the contract to try to send 0 when making a payout.
Payouts will become completely bricked, with no way to recover since fundingTotals can't be set anywhere else.
Submitting as high because it can be used in conjunction with methods of breaking refunds to permanently trap user funds.
Payouts are permanently bricked

## Recommendation
Add two fixes:
1) If a deposit is refunded and the contract has no tokens left then remove that token from the list of tokens
2) Add a condition to _transferERC20 that only transfers if _volume != 0
