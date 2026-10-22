# [M] A malicious market owner/protocol owner can steal lender funds

## Summary
Severity: Medium
Contest weight: 0.6006
Dataset id: 19955
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious market owners and protocol owners can arbitrarily set fees to extraordinary rates to steal all of the lenders funds.
A malicious market owner can front-run lenders who wish to accept a bid through lenderAcceptBid by calling MarketRegistry.setMarketFeePercent to set the marketplace fee to 100%. This allows the malicious market owner to steal 100% of the funds from the lender. The same thing can be done by a malicious protocol owner by calling ProtocolFee.setProtocolFee.
Lender loses all their funds on a bid they accept due to malicious or compromised market owner/protocol owner.
```solidity
function lenderAcceptBid(uint256 _bidId)
    external
    override
    pendingBid(_bidId, "lenderAcceptBid")
    whenNotPaused
    returns (
        uint256 amountToProtocol,
        uint256 amountToMarketplace,
        uint256 amountToBorrower
    )
{
    //..
    amountToProtocol = bid.loanDetails.principal.percent(protocolFee());
    amountToMarketplace = bid.loanDetails.principal.percent(
        marketRegistry.getMarketplaceFee(bid.marketplaceId)
    );
    // subtracting the fees from the principal value.
    amountToBorrower =
        bid.loanDetails.principal -
        amountToProtocol -
        amountToMarketplace;
    bid.loanDetails.lendingToken.safeTransferFrom(
        sender,
        owner(),
        amountToProtocol
    );
    bid.loanDetails.lendingToken.safeTransferFrom(
        sender,
        marketRegistry.getMarketFeeRecipient(bid.marketplaceId),
        amountToMarketplace
    );
    //..
}
```
```solidity
function setMarketFeePercent(uint256 _marketId, uint16 _newPercent)
    public
    ownsMarket(_marketId)
{
    require(_newPercent >= 0 && _newPercent <= 10000, "invalid percent");
    if (_newPercent != markets[_marketId].marketplaceFeePercent) {
        markets[_marketId].marketplaceFeePercent = _newPercent;
        emit SetMarketFee(_marketId, _newPercent);
    }
}
```

## Recommendation
1. Add a timelock delay for setMarketFeePercent/setProtocolFee.
2. Allow lenders to specify the exact fees they were expecting as a parameter to lenderAcceptBid.
"Market owners should NOT be able to race-condition attack borrowers or lenders by changing market settings while bids are being submitted or accepted (while tx are in mempool). Care has been taken to ensure that this is not possible (similar in theory to sandwich attacking but worse as if possible it could cause unexpected and non-consensual interest rate on a loan) and further-auditing of this is welcome. The best way to defend against this is to allow borrowers and lenders to specify such loan parameters in their TX such that they are explicitly consenting to them in the tx and then reverting if the market settings conflict with those tx arguments."
