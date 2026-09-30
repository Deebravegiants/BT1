# [H] Incorrect prefundingRefundcalculation will dis-

## Summary
Severity: High
Contest weight: 0.8857
Dataset id: 22634
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Incorrect prefundingRefund calculation will lead to underflow and hence disallowing claiming
The prefundingRefund variable calculation inside the claimProceeds function is incorrect
```solidity
function claimProceeds(
    uint96 lotId_,
    bytes calldata callbackData_
) external override nonReentrant {
    ...
    (uint96 purchased_, uint96 sold_, uint96 payoutSent_) = _getModuleForId(lotId_).claimProceeds(lotId_);
    ...
    // Refund any unused capacity and curator fees to the address dictated by the callbacks address
    // By this stage, a partial payout (if applicable) and curator fees have been paid, leaving only the payout amount (`totalOut`) remaining.
    uint96 prefundingRefund = routing.funding + payoutSent_ - sold_;
    unchecked {
        routing.funding -= prefundingRefund;
    }
```
Here sold is the total base quantity that has been sold to the bidders. Unlike required, the routing.funding variable need not be holding capacity + (0,curator fees) since it is decremented every time a payout of a bid is claimed
```solidity
function claimBids(uint96 lotId_, uint64[] calldata bidIds_) external override nonReentrant {
    ...
    if (bidClaim.payout > 0) {
        ...
        // Reduce funding by the payout amount
        unchecked {
            routing.funding -= bidClaim.payout;
        }
```
Example
Capacity = 100 prefunded, hence routing.funding == 100 initially Sold = 90 and no partial fill/curation All bidders claim before the claimProceed function is invoked Hence routing.funding = 100 - 90 == 10 When claimProceeds is invoked, underflow and revert:
uint96 prefundingRefund = routing.funding + payoutSent_ - sold_ == 10 + 0 - 90
Claim proceeds function is broken. Sellers won't be able to receive the proceedings

## Recommendation
Change the calculation to:
```solidity
uint96 prefundingRefund = capacity - sold_ + curatorFeesAdjustment (how much was prefunded initially - how much will be sent out based on capacity - sold)
```
