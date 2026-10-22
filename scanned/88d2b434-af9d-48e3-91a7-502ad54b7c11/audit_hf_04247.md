# [M] Function `addNewTranche`

## Summary
Severity: Medium
Contest weight: 0.5713
Dataset id: 21170
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
if (_renegotiationOffer.fee > 0) {
    /// @dev Cached
    ProtocolFee memory protocolFee = _protocolFee;
    ERC20(_loan.principalAddress).safeTransferFrom(
        _renegotiationOffer.lender,
        protocolFee.recipient,
        _renegotiationOffer.fee.mulDivUp(protocolFee.fraction, _PRECISION) // @audit Use protocolFee from Loan instead
    );
}
```

The protocol fee value is recorded and stored in the Loan struct when a new loan is issued. However, when adding a new tranche, the function uses the current value of `protocolFee.fraction` instead of the value stored in the Loan struct. This could result in inconsistencies in fee collection, as the protocol fee value might be updated by the admin, while the value stored in the Loan struct remains unchanged.

## Proof of Concept
The protocol fee value is stored in the Loan struct when a new loan is opened.

```solidity
function _processOffersFromExecutionData(
  ...
) ... {
  Loan memory loan = Loan(
      _borrower,
      _tokenId,
      _nftCollateralAddress,
      _principalAddress,
      totalAmount,
      block.timestamp,
      _duration,
      tranche,
      protocolFee.fraction
  );
}
```

## Recommendation
Consider using `_loan.protocolFee` instead of `protocolFee.fraction` in the `addNewTranche()` function.

`addNewTranche` uses `protocolFee` from struct.
