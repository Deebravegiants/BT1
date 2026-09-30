# [M] M-03 | Decaying Redemption Fee Manipulation

## Summary
Severity: Medium
Contest weight: 0.2039
Dataset id: 2255
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the leveraged token system a decaying redemption fee is applied to users who have recently deposited. Throughout the codebase the decaying redemption fee is assigned to start off at a 1% fee and decay to 0% over the course of 5 minutes. The minimum deposit for a user which will reset the timer for the decaying redemption fee is set to 5 USD in the Config contract as the DECAYING_REDEMPTION_MIN_BASE_AMOUNT value. With these conﬁgured parameters it can be signiﬁcantly proﬁtable for one vault depositor to do a small deposit on behalf of another depositor who is about to redeem and cause them to experience a signiﬁcant decay fee. The malicious vault depositor in this case (and the rest of LeveragedToken holders) would gain from the signiﬁcant fee paid by the victim depositor in this case. On networks without a public mempool speciﬁcally frontrunning a user’s withdrawal transaction is not reliably possible so this attack may operate based upon key indicators that a user is about to withdraw such as Discord messages or market volatility. Furthermore, if the DECAYING_REDEMPTION_MIN_BASE_AMOUNT is conﬁgured too high, then a depositor could simply deposit DECAYING_REDEMPTION_MIN_BASE_AMOUNT - 1 wei multiple times to avoid the decaying redemption fee while still depositing a large amount. This could occur in a single transaction with a multicall or for-loop contract call around the mintFor function.

## Recommendation
Configure the DECAYING_REDEMPTION_MIN_BASE_AMOUNT, decayingRedemptionFeeStart and decayingRedemptionFeeDuration with these behaviors in mind. Ensuring that the DECAYING_REDEMPTION_MIN_BASE_AMOUNT is neither too low to incentivize bad faith mints on behalf of other users and that the DECAYING_REDEMPTION_MIN_BASE_AMOUNT value is not too high to incentivize split deposits to avoid the decay fee measure.
