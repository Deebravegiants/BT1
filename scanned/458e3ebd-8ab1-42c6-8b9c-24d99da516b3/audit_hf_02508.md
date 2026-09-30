# [M] Improved Update of Boosted Borrow in NftCore::liquidate()

## Summary
Severity: Medium
Contest weight: 0.4605
Dataset id: 13391
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, the Whitehole protocol allows users to bid for an loan whose accumulated debt exceeds the liquidation threshold. The final winner of the auction can liquidate the loan by repaying the borrow for the borrower and get the pledged NFT asset. After the borrow is repaid for the borrower, it needs to update the boosted information for the borrower. Our analysis shows the boosted information of the borrower is not properly updated in the liquidation.
To elaborate, we show below the code snippets of the NftCore::liquidate()/Core::repayBorrow() routines. In the NftCore::liquidate() routine, it repays the borrow for the borrower by calling the core.repayBorrow() routine (line 273). In the Core::repayBorrow() routine, it updates the boosted information for the msg.sender (line 202). However, the msg.sender in the Core::repayBorrow() routine is actually the NftCore contract, not the borrower. As a result, the boosted information of the borrower is not updated.
```solidity
function liquidate(
    address gNft,
    uint256 tokenId
) external payable override onlyListedMarket(gNft) nonReentrant whenNotPaused {
    address nftAsset = IGNft(gNft).underlying();
    uint256 loanId = lendPoolLoan.getCollateralLoanId(nftAsset, tokenId);
    require(loanId > 0, "NftCore: collateral loan id not exist");
    Constant.LoanData memory loan = lendPoolLoan.getLoan(loanId);
    uint256 borrowBalance = lendPoolLoan.borrowBalanceOf(loanId);
    (uint256 extraDebtAmount, uint256 remainAmount) = validator.validateLiquidate(
        loanId, borrowBalance, msg.value
    );
    lendPoolLoan.liquidateLoan(gNft, loanId, borrowBalance);
    core.repayBorrow{value: borrowBalance}(borrowMarket, borrowBalance);
}

function repayBorrow(
    address gToken,
    uint256 amount
) external payable override onlyListedMarket(gToken) nonReentrant whenNotPaused {
    IGToken(payable(gToken)).repayBorrow{value: msg.value}(msg.sender, amount);
    grvDistributor.notifyBorrowUpdated(gToken, msg.sender);
}
```
Note the same issue is also applicable to the NftCore::redeem() routine.

## Recommendation
Revisit the above mentioned NftCore::liquidate()/redeem() routines to properly update the boosted information for the borrower.
