# [M] H-17 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-05-gondi-mitigation
Published: 2024-05-24
Source: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/95
Type: code-finding

## Details
# Lines of code

https://github.com/pixeldaogg/florida-contracts/blob/7212bfbe9f78ca6eabb5eec86e24d754feb47f15/src/lib/loans/MultiSourceLoan.sol#L1195


# Vulnerability details

### Impacts:
In an edge case, the same struct renegotiationOffer and renegotiaionOffer signature can still be used interchangeably between refinanceFull() and addNewTranche().

### Original Issue/ Current fix:
C4 Issue:
H-17: [refinanceFull/addNewTranche reusing a lender's signature leads to unintended behavior](https://github.com/code-423n4/2024-04-gondi-findings/issues/13)

Original vulnerabilities:
refinanceFull and addNewTranche both require RenegotiationOffer’s signature check, but allows the same renegotiationOffer struct and same signature to pass. 

Original impacts:
This encourages the attack vector of front-running to use the signature for malicious operations. In this case, an attacker can use the renegotiationOffer input and signature that was meant for refinanceFull() in addNewTranche(). 

Mitigation:
Fix: https://github.com/pixeldaogg/florida-contracts/pull/390/files
```solidity
//src/lib/loans/MultiSourceLoan.sol
    function refinanceFull(
        RenegotiationOffer calldata _renegotiationOffer,
        Loan memory _loan,
        bytes calldata _renegotiationOfferSignature
    ) external nonReentrant returns (uint256, Loan memory) {
        _checkRefinanceFullRenegotiationOffer(_renegotiationOffer, _loan.tranche.length);
...

    function addNewTranche(
        RenegotiationOffer calldata _renegotiationOffer,
        Loan memory _loan,
        bytes calldata _renegotiationOfferSignature
    ) external nonReentrant returns (uint256, Loan memory) {
...
        _checkAddNewTrancheOffer(_renegotiationOffer, _loan.tranche.length);


    function _checkAddNewTrancheOffer(RenegotiationOffer calldata _renegotiationOffer, uint256 _totalTranches)
        private
        pure
    {
|>       if (_renegotiationOffer.trancheIndex.length != 1 || _renegotiationOffer.trancheIndex[0] != _totalTranches) {
            revert InvalidRenegotiationOfferError();
        }
    }

    function _checkRefinanceFullRenegotiationOffer(
        RenegotiationOffer calldata _renegotiationOffer,
        uint256 _totalTranches
    ) private pure {
 |>     if (_renegotiationOffer.trancheIndex.length != _totalTranches) {
            revert InvalidRenegotiationOfferError();
        }
    }
```
The current fix is to add additional checks on struct renegotiationOffer. In r`efinanceFull()`, checks are added to ensure that `_renegotiationOffer.trancheIndex.length != _totalTranches` . In `addNewTranche()`, a different check is in place to make sure `tranchIndex.length ==1 && trancheIndex[0]== _totalTranches` (the only trancheIndex would be the next tranche index).

### Proof of concept

The problem is an edge case will still allow struct renegotiationOffer and renegotiaionOffer signature to be used interchangeably between refinanceFull() and addNewTranche().

Edge Case: 
A loan only has 1 tranche, and `_renegotiationOffer.trancheIndex[0] == 1`. 

When a loan has 1 tranche, _renegotiationOffer.trancheIndex.length == _totalTranches will be true. And as long as the _renegotiationOffer's trancheIndex[0] is _totalTranches/1, the _renegotiationOffer will pass both `_checkAddNewTrancheOffer()` and `_checkRefinanceFullRenegotiationOffer()`.

Note: in refinanceFull() flow, `_renegotiationOffer.trancheIndex[0]` is not used and not checked. So the value of `_renegotiationOffer.trancheIndex[0]` will not make a difference in `refinanceFull()`.
```solidity

    function _checkRefinanceFullRenegotiationOffer(
        RenegotiationOffer calldata _renegotiationOffer,
        uint256 _totalTranches
    ) private pure {
        //@audit when there is only one tranche in the loan, _renegotiationOffer.trancheIndex.length == _totalTranches == 1
 |>     if (_renegotiationOffer.trancheIndex.length != _totalTranches) {
            revert InvalidRenegotiationOfferError();
        }
    }
```

Impact: The lender’s renegotiationOffer for refinanceFull can still be used for addNewTranche(); And vice versa. 
(1) When a borrower wants to add a new tranche and receive the additional principal amount, instead, the lender might use the offer to `refinanceFull()` to avoid transferring the principal. 
(2) Or when a lender refinanceFull() for a loan with only 1 tranche and with input (_renegotiationOffer.trancheIndex[0] as 1). A malicious borrower can receive 100% more principal with existing NFT collateral - borrower's position will be significantly under-collateralized. Borrower might earn a profit even by giving up their NFT.

### Recommendations:
In `_checkRefinanceFullRenegotiationOffer()`, add check to ensure `renegotiationOffer.trancheIndex[0] != _totalTranches`.










## Assessed type

Other
