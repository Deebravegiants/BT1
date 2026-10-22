# [C] C-01 | Mishandled Donated Liquidity Breaks Rebalance

## Summary
Severity: Critical
Contest weight: 0.2598
Dataset id: 2100
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The removeAllFrom function in the BPOOLv1 contract is intended to handle any unexpected liquidity
(i.e., donations) by removing it from the position and then accounting for both the liquidity amount
and its fees in the total bAssetFees_, which is subsequently sent to the fee recipient.
However, the current implementation does not behave as intended. Instead, the donated amount is
burned in the internal removeLiquidity function while that same burned amount is also counted in
bAssetFees.
This discrepancy causes the MarketMaking contract’s bAsset balance to be lower than the total
bAssetFees_, leading to a revert when fees are transferred.
Because of this revert, the rebalance function fails to execute, preventing the protocol from adjusting
its liquidity to changing market conditions. Additionally, a malicious actor could intentionally exploit
this ﬂaw by donating, causing a DOS to the rebalance function.

## Proof of Concept
https://github.com/GuardianAudits/baseline-mm-2/blob/fb34449337782dc635e277bfed2b0d4db19aa185/test/guardian/DonationBurned.t.sol#L55

## Recommendation
Modify the implementation so that the donated liquidity is not burned and is correctly accounted for
and transferred to the fee recipient.
