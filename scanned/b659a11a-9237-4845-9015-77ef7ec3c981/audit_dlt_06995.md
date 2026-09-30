# [M] H-17 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-05-gondi-mitigation
Published: 2024-05-20
Source: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/18
Type: code-finding

## Details
# Lines of code




# Vulnerability details

https://github.com/pixeldaogg/florida-contracts/pull/390

This PR adds two methods to differentiate between the two:
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

1. `addNewTranche()` need :
` _renegotiationOffer.trancheIndex.length == 1 && _renegotiationOffer.trancheIndex[0] == _loan.tranche.length`
2. `refinanceFull()` need:
`_renegotiationOffer.trancheIndex.length == _loan.tranche.length`

The above conditions all pass the check if `_loan.tranche.length==1`, it still conflicts.

Exmaple: user sign "_renegotiationOffer.trancheIndex = [1]" will pass both

## Recommended Mitigation

The best way is add `type`, eg:  `_renegotiationOffer.type = add | full | part`

simple way limit `_checkRefinanceFullRenegotiationOffer()` like:

```diff
    function _checkRefinanceFullRenegotiationOffer(
        RenegotiationOffer calldata _renegotiationOffer,
        uint256 _totalTranches
    ) private pure {
-       if (_renegotiationOffer.trancheIndex.length != _totalTranches) {
+       if (_renegotiationOffer.trancheIndex.length != 0 || _renegotiationOffer.trancheIndex[0] != 0) {    
            revert InvalidRenegotiationOfferError();
        }
    }
```


## Assessed type

Context
