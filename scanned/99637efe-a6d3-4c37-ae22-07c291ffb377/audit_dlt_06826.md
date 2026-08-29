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
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-gondi-findings/issues/29_
