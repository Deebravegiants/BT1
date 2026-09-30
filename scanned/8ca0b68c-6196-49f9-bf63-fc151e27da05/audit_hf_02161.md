# [M] Potential Sandwich/MEV Attack In liquidate()

## Summary
Severity: Medium
Contest weight: 0.4449
Dataset id: 12077
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, if a borrower has not capability to repay his borrowed assets on time, his collateral assets will be liquidated by others. In particular, one entry routine, i.e., liquidate(), allows the lender to liquidate the borrower's collateral assets by himself. While examining its logic, we observe there is a vulnerability that can be exploited by the lender to decrease transaction fee. To elaborate, we show below the related code snippet of the FeedLoan contract. By design, the _lenderFee can be discounted (line 580) according to the amount of the token (specified by the token variable of the FeesController contract) held by the lender. If the amount of the token is larger than 50000000000000000 (line 66), the _lenderFee will be discounted to zero. By borrowing a huge of the token through flashloan before the call to liquidate(), the lender can reduce the transaction fee along with receiving more collateral assets than normal.
```solidity
function liquidate(uint256 _loanId) external nonReentrant {
    // Fetch loan from storage
    Loan storage _loan = loans[_loanId];
    // Loan should not be repaid, liquidated completed
    require(_loan.status == LoanStatus.Active, "FeedLoan(liquidate): Loan is not active");
    // Current block time is greater than loan starting time plus duration
    require(block.timestamp > _loan.startTime.add(_loan.duration), "FeedLoan(liquidate): Loan is not overdue");
    // Get loan's lender
    address _lender = loanLender[_loanId];
    // Only lender is allowed liquidate the loan
    require(_lender == msg.sender, "FeedLoan(liquidate): Sender is not lender");
    // Burn NFT
    _burn(_loanId);
    // Set loan
```

## Recommendation
Develop an effective mitigation to the above MEV attack. One possible mitigation is to ensure the liquidator is a EOA account.
