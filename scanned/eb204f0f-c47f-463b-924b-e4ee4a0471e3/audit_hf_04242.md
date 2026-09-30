# [H] `_processOffersFromExecutionData

## Summary
Severity: High
Contest weight: 0.2594
Dataset id: 21163
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`emitLoan()` only limits `offer.duration != 0`. There’s no limit in `executionData.duration<=offer.duration`.

`emitLoan()` -> `_processOffersFromExecutionData()` -> `_validateOfferExecution()`
```
    function _validateOfferExecution(
        OfferExecution calldata _offerExecution,
        uint256 _tokenId,
        address _lender,
        address _offerer,
        bytes calldata _lenderOfferSignature,
        uint256 _feeFraction,
        uint256 _totalAmount
    ) private {
...

        if (offer.duration == 0) {
            revert ZeroDurationError();
        }
        if (offer.aprBps == 0) {
            revert ZeroInterestError();
        }
        if ((offer.capacity > 0) && (_used[_offerer][offer.offerId] + _offerExecution.amount > offer.capacity)) { 
            revert MaxCapacityExceededError();
        }

        _checkValidators(_offerExecution.offer, _tokenId);
    }
```
If the `executionData.duration` time is not limited, it can lead to far exceeding the borrowing time `offer.duration`. If the `lender` is a `LoanManager`, when `repayLoan()` it can also exceed the maximum `pendingQueues`, leading to accounting issues.

## Recommendation
Check `executionData.duration<=offer[n].duration`.
