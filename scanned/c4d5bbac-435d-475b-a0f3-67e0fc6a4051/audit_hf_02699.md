# [C] Bids only transfer collateral for the ﬁrst token type

## Summary
Severity: Critical
Contest weight: 0.2997
Dataset id: 14644
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a bid is submitted, its validity is assessed against all the different collateral tokens in the bid added together.
However, only the ﬁrst collateral token is actually transferred.
A user could submit a large bid with collateral in two tokens: A and B. The amount of token A could be tiny and the amount of token B could be very large. The system would accept the submitted bid and potentially allow this user to borrow a large amount of the purchase token whilst only making the small token A collateral payment.
The function which assesses whether a bid has sufficient collateral is TermAuctionBidLocker._isInInitialCollateralShortFall().
On line [434], this function loops through the array collateralTokens_, calculates their cumulative value, and on line [450] compares this to the bid’s repurchase price.
The code which stores an accepted bid only processes the ﬁrst collateral token, however. This code is on line [231] to line [272] and it consistently assesses only bidSubmission.collateralTokens[0] and bidSubmission.collateralAmounts[0], including, crucially, in the calls to termRepoCollateralManager.auctionLockCollateral() where the collateral tokens are transferred.

## Recommendation
If multiple collateral tokens are allowed in a bid, modify the code of _lock() to process multiple tokens at each step.
If only one collateral token is to be allowed per bid, review and modify the code of TermAuctionBidLocker.sol.
Consider that the system may be signiﬁcantly simpliﬁed by limiting bids to only one kind of collateral token. Multiple collateral bids may be rare, and yet they add signiﬁcant system complexity which results in higher gas costs and the potential for further security issues. A user could still submit multiple separate bids in the same auction using diﬀerent collateral tokens.
