# [H] Function `distribute`

## Summary
Severity: High
Contest weight: 0.8068
Dataset id: 21151
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `LiquidationDistributor` contract manages the distribution of funds after a liquidation auction is settled. It distributes the received funds to the lenders of the loan. If the lender has implemented the `LoanManager` interface, it will also call `loanLiquidation()` on the lender’s address. The Pool, when `loanLiquidation()` is called, will conduct an accounting process to ensure that the received funds are fairly distributed to the depositors.
```solidity
function loanLiquidation(
    uint256 _loanId,
    uint256 _principalAmount,
    uint256 _apr,
    uint256,
    uint256 _protocolFee,
    uint256 _received,
    uint256 _startTime
) external override onlyAcceptedCallers {
    uint256 netApr = _netApr(_apr, _protocolFee);
    uint256 interestEarned = _principalAmount.getInterest(netApr, block.timestamp - _startTime);
    uint256 fees = IFeeManager(getFeeManager).processFees(_received, 0);
    getCollectedFees += fees;
    // @audit Accounting logic
    _loanTermination(msg.sender, _loanId, _principalAmount, netApr, interestEarned, _received - fees);
}
```
However, the `distribute()` function lacks access control. Consequently, an attacker could directly call it with malicious data, leading to incorrect accounting in the Pool.

## Proof of Concept
Observe how the `loanLiquidation()` function is called:
```solidity
function _handleLoanManagerCall(IMultiSourceLoan.Tranche calldata _tranche, uint256 _sent) private {
    if (getLoanManagerRegistry.isLoanManager(_tranche.lender)) {
        LoanManager(_tranche.lender).loanLiquidation(
            _tranche.loanId,
            _tranche.principalAmount,
            _tranche.aprBps,
            _tranche.accruedInterest,
            0,
            _sent,
            _tranche.startTime
        );
    }
}
```
As shown above, the `principalAddress` is not passed in, meaning it will not be validated by the Pool. Therefore, an attacker can simply call the `distribute()` function with `loan.principalAddress` set to a random ERC20 token. This token will still be transferred to the Pool. However, the Pool will mistake this token as its asset token (USDC/WETH) and perform the accounting accordingly.

## Recommendation
Only allow Loan contracts to call the `distribute()` function.
