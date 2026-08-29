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
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/95_
