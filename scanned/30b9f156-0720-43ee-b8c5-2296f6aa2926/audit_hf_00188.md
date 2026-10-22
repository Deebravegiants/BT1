# [M] hard to clear balance

## Summary
Severity: Medium
Contest weight: 0.0867
Dataset id: 1003
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract does not allow users to transfer by share. Therefore, it is hard for users to clear out all the shares. There will be users using this token with Metamask and it is likely the `pricePerShare` would increase after the user sends transactions. I consider this is a medium-risk issue.

## Proof of Concept
[WrappedIbbtc.sol#L110-L118](https://github.com/code-423n4/2021-10-badgerdao/blob/main/contracts/WrappedIbbtc.sol#L110-L118)

## Recommendation
A new `transferShares` beside the original `transfer()` would build a better UX. sushi’s bento box would be a good ref [BentoBox.sol](https://github.com/sushiswap/bentobox/blob/master/contracts/BentoBox.sol)
