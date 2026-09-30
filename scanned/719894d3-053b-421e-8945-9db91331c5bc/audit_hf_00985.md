# [M] Supporting fee-on-transfer tokens can lead to bad debt

## Summary
Severity: Medium
Contest weight: 0.1638
Dataset id: 3074
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol claims it can support fee-on-transfer (FOT) tokens if necessary. According to the pre-audit questionlist:
- If enabled, the collateral and liquidation factors
- (haircut on the value) will be adjusted to accommodate for the value loss due to fee
The issue is that changing the liquidation and collateral factors will not be enough to resolve the issue. This can be explained by a simple example.
Say Token A is a FOT token, with a 1% fee.
1. Alice deposits 100,000 tokens of token A.
2. Contract receives 99,000 tokens, but credits Alice's account with the full 100,000 tokens
3. Alice now withdraws 99,000 tokens
4. Alice receives 89,100 tokens after fees. Contract has 0 tokens, since it paid out all its holdings, but contract still thinks that it holds (100,000 - 99,000)=1,000 tokens.
5. Alice can now take out a loan against those 1,000 tokens which the contract thinks it holds. This is entirely bad debt.
With deposits and successive withdrawals, FOT tokens can be used to create bad debt positions at very minimal costs. Since this directly affects the health of the system, this is a problem.

## Recommendation
FOT tokens should always be used with post-transfer accounting logic. Since the protocol doesn't have that, it is recommended not to support FOT tokens at all, despite the claim in the Questionlist.
