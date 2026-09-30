# [M] M-02 | Redeemer Avoids Paying The Streaming Fee

## Summary
Severity: Medium
Contest weight: 0.1636
Dataset id: 2254
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Within the LeveragedToken’s redeemFor ﬂow, the contract calculates:
• baseWithdrawn = (leveragedTokenAmount * exchangeRate) - decayingRedemptionFee - slippage.
• Then it calls _withdrawMargin(baseWithdrawn + streamingFee).
• Lastly, it charges the streaming fee (_chargeStreamingFee(streamingFee)) out of the contract’s Synthetix margin.
However, the user’s baseWithdrawn portion is based on an exchange rate computed before the streaming fee is removed from margin and consequently the user does not pay his pro-rata share of that streaming fee. All holders end up paying the streaming fee out of the leftover margin collectively, while the redeemer takes out margin as if no fee had been deducted. By computing baseWithdrawn from the pre-fee exchangeRate, the user is granted a higher share. The streaming fee is then subtracted from the contract’s margin but not from the user’s ﬁnal redemption proceeds.

## Proof of Concept
https://github.com/GuardianAudits/snx-leveraged-tokens-1/commit/fbeddc0dc032495e7186d330c0a4a5f614b32a35

## Recommendation
Consider reducing the the user’s baseWithdrawn by their portion of the streaming fee. For example, if the user holds X% of the total supply, they pay X% of the streaming fee in the redemption step. On the other hand, consider also implementing a function that is called frequently to charge the streaming fee manually.
