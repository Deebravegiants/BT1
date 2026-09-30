# [M] Potential DoS in NftCore::redeem()/auction()

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 13390
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Whitehole protocol allows users to borrow assets using NFTs as the underlying collateral. When the loan's accumulated debt exceeds the liquidation threshold, the loan can be auctioned. It selects the latest bid winner who offers the highest bid for the auction by now. Everytime a new winner is generated, it returns the bid back to the previous winner. Our analysis shows that the current implementation to refund the previous winner has a potential denial-of-service issue.
To elaborate, we show below the code snippet of the auction() routine, which is used for a bidder to bid for an auction. Because the borrower can only borrow ETH with NFTs as the underlying collateral, so the bid and refund are both in ETH. However, it comes to our attention that the malicious bidder can be a contract that does not implement the receiver()/fallback() routines to accept ETH. In this case, the refund will revert (line 216), and the auction will not accept new bidders before the end of the auction. As a result, the malicious bidder will win the auction at last. We therefore suggest to allow only EOA accounts to join the auction or design a strong mechanism to refund the bidder.
```solidity
function auction(
    address gNft,
    uint256 tokenId
) external payable override onlyListedMarket(gNft) nonReentrant whenNotPaused {
    address nftAsset = IGNft(gNft).underlying();
    uint256 loanId = lendPoolLoan.getCollateralLoanId(nftAsset, tokenId);
    require(loanId > 0, "NftCore: collateral loan id not exist");
    Constant.LoanData memory loan = lendPoolLoan.getLoan(loanId);
    uint256 borrowBalance = lendPoolLoan.borrowBalanceOf(loanId);
    validator.validateAuction(gNft, loanId, msg.value, borrowBalance);
    lendPoolLoan.auctionLoan(msg.sender, loanId, msg.value, borrowBalance);
    if (loan.bidderAddress != address(0)) {
        SafeToken.safeTransferETH(loan.bidderAddress, loan.bidPrice);
        emit Auction(...);
    }
}
```
Note the same issue is also applicable to the NftCore::redeem() routine.

## Recommendation
Revise the above mentioned routines in the NftCore contract to avoid the above denial-of-service situation.
