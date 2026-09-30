# [H] liquidateDefaultedLoanWithIncentive sends

## Summary
Severity: High
Contest weight: 0.7856
Dataset id: 22749
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
liquidateDefaultedLoanWithIncentive sends the collateral to the Lender - LenderCommitmentGroup (LCG) instead of the liquidator. Liquidators will not be incentivized to liquidate. liquidateDefaultedLoanWithIncentive is intended to liquidate bids, where liquidators pay off the debt and receive the collateral. However, currently the collateral is sent to the lender - LCG, because lenderCloseLoanWithRecipient includes msg.sender as its second parameter but does not utilize it:
```solidity
function lenderCloseLoanWithRecipient(uint256 _bidId, address _collateralRecipient) external {
    _lenderCloseLoanWithRecipient(_bidId, _collateralRecipient);
}

function _lenderCloseLoanWithRecipient(uint256 _bidId, address _collateralRecipient) internal acceptedLoan(_bidId, "lenderClaimCollateral")
{
    require(isLoanDefaulted(_bidId), "Loan must be defaulted.");
    Bid storage bid = bids[_bidId];
    bid.state = BidState.CLOSED;
    address sender = _msgSenderForMarket(bid.marketplaceId);
    require(sender == bid.lender, "Only lender can close loan");
    collateralManager.lenderClaimCollateral(_bidId);
}
```
lenderClaimCollateral in its place withdraws the collateral directly to the lender - LCG, without updating totalPrincipalTokensRepaid. Some effects:
• Liquidators will gain 0 profits, so they will not liquidate.
• LPs suffer losses as liquidations are not carried out, and returned collateral from liquidations is not accrued as totalPrincipalTokensRepaid, increasing utilization, eventually bricking the contract.
Liquidators will not be incentivized to liquidate and incorrect accounting occurs inside LCG.
```solidity
function _lenderCloseLoanWithRecipient(
    uint256 _bidId,
) internal acceptedLoan(_bidId, "lenderClaimCollateral") {
    require(isLoanDefaulted(_bidId), "Loan must be defaulted.");
    Bid storage bid = bids[_bidId];
    bid.state = BidState.CLOSED;
    address sender = _msgSenderForMarket(bid.marketplaceId);
    require(sender == bid.lender, "Only lender can close loan");
    collateralManager.lenderClaimCollateral(_bidId);
}
```

## Recommendation
Ensure _lenderCloseLoanWithRecipient sends the funds to _collateralRecipient.
