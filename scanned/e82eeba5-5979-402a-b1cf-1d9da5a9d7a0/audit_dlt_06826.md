# [H] addNewTranche() no authorization from borrower

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-gondi
Published: 2024-04-16
Source: https://github.com/code-423n4/2024-04-gondi-findings/issues/29
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-gondi/blob/b9863d73c08fcdd2337dc80a8b5e0917e18b036c/src/lib/loans/MultiSourceLoan.sol#L358


# Vulnerability details

## Vulnerability details
`addNewTranche() ` The code implementation is as follows：
```solidity
    function addNewTranche(
        RenegotiationOffer calldata _renegotiationOffer,
        Loan memory _loan,
        bytes calldata _renegotiationOfferSignature
    ) external nonReentrant returns (uint256, Loan memory) {
        uint256 loanId = _renegotiationOffer.loanId;

        _baseLoanChecks(loanId, _loan);
        _baseRenegotiationChecks(_renegotiationOffer, _loan);
@>      _checkSignature(_renegotiationOffer.lender, _renegotiationOffer.hash(), _renegotiationOfferSignature);
        if (_loan.tranche.length == getMaxTranches) {
            revert TooManyTranchesError();
        }

        uint256 newLoanId = _getAndSetNewLoanId();
        Loan memory loanWithTranche = _addNewTranche(newLoanId, _loan, _renegotiationOffer);
        _loans[newLoanId] = loanWithTranche.hash();
        delete _loans[loanId];

        ERC20(_loan.principalAddress).safeTransferFrom(
            _renegotiationOffer.lender, _loan.borrower, _renegotiationOffer.principalAmount - _renegotiationOffer.fee
        );
        if (_renegotiationOffer.fee > 0) {
            /// @dev Cached
            ProtocolFee memory protocolFee = _protocolFee;
            ERC20(_loan.principalAddress).safeTransferFrom(
                _renegotiationOffer.lender,
                protocolFee.recipient,
                _renegotiationOffer.fee.mulDivUp(protocolFee.fraction, _PRECISION)
            );
        }

        emit LoanRefinanced(
            _renegotiationOffer.renegotiationId, loanId, newLoanId, loanWithTranche, _renegotiationOffer.fee
        );

        return (newLoanId, loanWithTranche);
    }
```
Currently only the signature of the `lender` is checked, not the authorization of the `borrower`.
Then any `lender` can add `tranche` to any `loan` by
1. specify a very high apr
2. specify any `_renegotiationOffer.fee`,example : set `_renegotiationOffer.fee==_renegotiationOffer.principalAmount`.

This doesn't make sense for `borrower`.

It is recommended that only the `borrower` performs this method.

## Impact

`lender` can be specified to generate a malicious `tranche` to compromise `borrower`.

## Recommended Mitigation

```diff
    function addNewTranche(
        RenegotiationOffer calldata _renegotiationOffer,
        Loan memory _loan,
        bytes calldata _renegotiationOfferSignature
    ) external nonReentrant returns (uint256, Loan memory) {
        uint256 loanId = _renegotiationOffer.loanId;
+       if (msg.sender != _loan.borrower) {
+           revert InvalidCallerError();
+       } 
        _baseLoanChecks(loanId, _loan);
        _baseRenegotiationChecks(_renegotiationOffer, _loan);
        _checkSignature(_renegotiationOffer.lender, _renegotiationOffer.hash(), _renegotiationOfferSignature);
        if (_loan.tranche.length == getMaxTranches) {
            revert TooManyTranchesError();
        }
```


## Assessed type

Context
