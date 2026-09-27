# [H] H-17 Unmitigated

## Summary
Severity: High
Chain: Smart contract
Component: 2024-05-gondi-mitigation
Published: 2024-05-24
Source: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/65
Type: code-finding

## Details
# Lines of code

https://github.com/pixeldaogg/florida-contracts/blob/10d48b51313496c41c886cd46e610b627ef159aa/src/lib/loans/MultiSourceLoan.sol#L1172-L1188


# Vulnerability details

## Issue

The `refinanceFull()` and `addNewTranche()` functions share the same signature. This could lead to an issue where a user signs a signature for a full refinance, but it gets used in `addNewTranche()`. This could inadvertently increase the principal amount of the loan, which may not be the user's intention.

## Mitigation

The fix did differentiating between the two functions by using the length of `trancheIndex` and the value of `trancheIndex[0]`.

- addNewTranche: The length of the `trancheIndex` must be `1`, and its value is `_totalTranches`. This should result in an out-of-bound error if it's used in refinance.
- refinanceFull: The length of `trancheIndex` must be equal to `_totalTranches`.

With this check in place, I believe the `RenegotiationOffer` for a loan with 1 tranche can still be used for both functions. This is because `trancheIndex` isn't actually used in `refinanceFull`, but only in `refinancePartial`. So the out-of-bound exception will not be raised in `refinanceFull`

```solidity
function _checkAddNewTrancheOffer(RenegotiationOffer calldata _renegotiationOffer, uint256 _totalTranches)
    private
    pure
{
    if (_renegotiationOffer.trancheIndex.length != 1 || _renegotiationOffer.trancheIndex[0] != _totalTranches) {
        revert InvalidRenegotiationOfferError();
    }
}

function _checkRefinanceFullRenegotiationOffer(
    RenegotiationOffer calldata _renegotiationOffer,
    uint256 _totalTranches
) private pure {
    if (_renegotiationOffer.trancheIndex.length != _totalTranches) {
        revert InvalidRenegotiationOfferError();
    }
}
```



## Assessed type

Other
