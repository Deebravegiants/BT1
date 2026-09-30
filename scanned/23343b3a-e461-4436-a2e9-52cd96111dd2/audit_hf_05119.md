# [M] Funding Paid != Funding Received The protocol has acknowledged this issue.

## Summary
Severity: Medium
Reporter: 0x37, 0xbranded, bughuntoor
Contest weight: 0.2559
Dataset id: 23163
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to special requirements around receiving funding fees for a position, the funding fees received can be less than that paid. These funding fee payments are still payed, but a portion of them will not be withdrawn, and become stuck funds. This also violates the contract specification that sum(funding_received) = sum(funding_paid).
In calc_fees there are two special conditions that impact a position's receipt of funding payments:
If the position has run out of collateral by the time it is being closed, he will receive none of his share of funding payments. Additionally, if the available collateral is not high enough to service the funding fee receipt, he will receive only the greatest amount that is available.
These funding fee payments are still always made (deducted from remaining collateral), whether they are received or not:
When a position is closed under most circumstances, the pool will have enough collateral to service the corresponding fee payment:
When positions are closed, the original collateral (which was placed into the pool upon opening) is removed. However, the amount of funding payments a position made is added to the pool for later receipt. Thus, when positions are still open there is enough position collateral to fulfill the funding fee payment and when they close the funding payment made by that position still remains in the pool.
Only when the amount of funding a position paid exceeded its original collateral, will there will not be enough collateral to service the receipt of funding fees, as alluded to in borrow fee exceeds the collateral balance remaining thereafter, they will not receive any funding fees. As a result, it's possible for funding fees to be paid which are never received.
Further, even in the case of funding fee underpayment, setting the funding fee received to 0 does not remedy this issue. The funding fees which he underpaid were in a differing token from those which he would receive, so this only furthers the imbalance of fees received to paid.
core.vy includes a specification for one of the invariants of the protocol:
This invariant is clearly broken as some portion of paid funding fees will not be received under all circumstances, so code is not to spec. This will also lead to some stuck funds, as a portion of the paid funding fees will never be deducted from the collateral. This can in turn lead to dilution of fees for future funding fee recipients, as the payments will be distributed evenly to the entire collateral including these stuck funds which will never be removed.

## Recommendation
Consider an alternative method of accounting for funding fees, as there are many cases under the current accounting where fees received/paid can fall out of sync.
For example, include a new state variable that explicitly tracks unpaid funding fee payments and perform some pro rata or market adjustment to future funding fee recipients, specifically for that token.
