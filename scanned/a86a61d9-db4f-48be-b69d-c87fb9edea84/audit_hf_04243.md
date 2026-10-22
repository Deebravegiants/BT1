# [H] `mergeTranches

## Summary
Severity: High
Contest weight: 0.3683
Dataset id: 21164
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `mergeTranches()`, the method’s code implementation is as follows:
```
 function mergeTranches(uint256 _loanId, Loan memory _loan, uint256 _minTranche, uint256 _maxTranche)
        external
        returns (uint256, Loan memory)
    {
        _baseLoanChecks(_loanId, _loan);
        uint256 loanId = _getAndSetNewLoanId();
        Loan memory loanMergedTranches = _mergeTranches(loanId, _loan, _minTranche, _maxTranche);
        _loans[loanId] = loanMergedTranches.hash();
        delete _loans[_loanId];

        emit TranchesMerged(loanMergedTranches, _minTranche, _maxTranche);

        return (loanId, loanMergedTranches);
    }
```
As shown above, this method lacks reentrancy protection, which could allow reentrancy attacks to manipulate the `_loans[]`.

Example: Suppose `_loans[1] = {NFT = 1}`

1. Alice calls `refinanceFromLoanExecutionData(_loans[1],LoanExecutionData)`.

   * `LoanExecutionData.ExecutionData.OfferExecution.LoanOffer.OfferValidator[0].validator` = CustomContract => for callback`.
2. `refinanceFromLoanExecutionData()` -> `_processOffersFromExecutionData()` -> `_validateOfferExecution()` -> `_checkValidators()` -> `IOfferValidator(CustomContract).validateOffer()`.
3. In `IOfferValidator(CustomContract).validateOffer()`, call `MultiSourceLoan.mergeTranches(_loans[1])` -> pass without `nonReentrant`.

   * `_loans[3] = newLoan.hash()`
4. Return to `refinanceFromLoanExecutionData()`, will execute:

   * `_loans[2] = newOtherLoan.hash()`.

There will be `_loans[2]` and `_loans[3]`, both containing `NFT=1`. Note: Both Loans ‘s lender are all himself:

1. The user can `repayLoan(_loans[2])` and get the NFT back.
2. Use the NFT to borrow other people’s funds, e.g. to generate `_loans[100]`.
3. `repayLoan(_loans[3])`, get NFT back.

## Recommendation
Add `nonReentrant`:
```
 function mergeTranches(uint256 _loanId, Loan memory _loan, uint256 _minTranche, uint256 _maxTranche)
        external
        nonReentrant
        returns (uint256, Loan memory)
    {
        _baseLoanChecks(_loanId, _loan);
        uint256 loanId = _getAndSetNewLoanId();
```
```
    function refinancePartial(RenegotiationOffer calldata _renegotiationOffer, Loan memory _loan)
        external
        nonReentrant
        returns (uint256, Loan memory)
    {
```
