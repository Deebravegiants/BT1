# [M] Improper Logic Of liquidateOnBehalf()

## Summary
Severity: Medium
Contest weight: 0.4591
Dataset id: 12076
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, if a borrower has not capability to repay his borrowed assets on time, his collateral assets will be liquidated by others. In particular, one entry routine, i.e., liquidateOnBehalf(), allows others to liquidate the borrower's collateral assets on behalf of the lender. While examining its logic, we notice there is an improper implementation that needs to be improved. To elaborate, we show below the related code snippet of the FeedLoan contract. By design, during liquidating the borrower's collateral assets, the part of the repaid assets (specified by the _lenderFee and _borrowerFee variables) will be respectively transferred to lenderFeeCollector (line 510) and borrowerFeeCollector (line 513) as transaction fee. However, we notice _lenderFee is incorrectly transferred to borrowerFeeCollector, which directly undermines the original intention of design. Given this, we suggest to correct the implementation as below: IERC20(_loan.asset).safeTransferFrom(address(msg.sender), address(borrowerFeeCollector), borrowerFeeCollector) (line 513).
```solidity
function liquidateOnBehalf(uint256 _loanId) external nonReentrant {
    // Fetch loan from storage
    Loan storage _loan = loans[_loanId];
    // Check whether lender allow liquidator liquidate loan
    require(_loan.allowLiquidator, "FeedLoan(liquidateOnBehalf): Liquidator is not allowed");
    // Loan should not be repaid, liquidated completed
    require(_loan.status == LoanStatus.Active, "FeedLoan(liquidateOnBehalf): Loan is not active");
    // Current block time is greater than loan starting time plus duration
    require(block.timestamp > _loan.startTime.add(_loan.duration), "FeedLoan(liquidateOnBehalf): Loan is not overdue");
    uint256 _interestDue = _loan.maxRepayment.sub(_loan.assetAmount);
    if (_loan.intProRated) {
        _interestDue = _calcInterestDue(
            _loan.assetAmount,
            _loan.intRateBP,
            _loan.duration,
            block.timestamp.sub(_loan.startTime),
            _loan.intProRated
        );
    }
    uint256 _lenderFee = _interestDue.mul(lenderFeeBP).div(10000);
    uint256 _borrowerFee = _interestDue.mul(borrowerFeeBP).div(10000);
    // If fees controller is set, adjust lender and borrower fees accordingly
    if (feesController != address(0)) {
        // Calculate and set lender & borrower fee by using discount basis point from FeesController
        _lenderFee = _lenderFee.sub(_lenderFee.mul(IFeesController(feesController).getDiscountBP(loanLender[_loanId])).div(10000));
        _borrowerFee = _borrowerFee.sub(_borrowerFee.mul(IFeesController(feesController).getDiscountBP(address(msg.sender))).div(10000));
    }
    uint256 _repaymentAmount = _loan.assetAmount.add(_interestDue).sub(_lenderFee.add(_borrowerFee));
    // Transfer principal including interest from liquidator contract
    uint256 _assetAmount = _safeDeflationaryTransfer(address(msg.sender), address(this), _loan.asset, _repaymentAmount);
    // Update loan asset amount in case token is deflationary
    _loan.assetAmount = _assetAmount.sub(_interestDue.sub(_lenderFee.add(_borrowerFee)));
    // Transfer lender's fee
    IERC20(_loan.asset).safeTransferFrom(address(msg.sender), address(lenderFeeCollector), _lenderFee);
    // Transfer borrower's fee
    IERC20(_loan.asset).safeTransferFrom(address(msg.sender), address(borrowerFeeCollector), _lenderFee);
```

## Recommendation
Correct the above implementation in liquidateOnBehalf().
