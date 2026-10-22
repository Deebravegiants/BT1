# [M] migrateV3Loan() will revert for lenders that are approved or use ERC-1271

## Summary
Severity: Medium
Contest weight: 0.4179
Dataset id: 3033
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
migrateV3Loan() checks that externalSigner, the address retrieved from the signature, is the same as the lender address:
```solidity
function migrateV3Loan(
    uint256 oldLoanId,
    LoanLibrary.LoanTerms calldata newTerms,
    address lender,
    Signature calldata sig,
    SigProperties calldata sigProperties,
    LoanLibrary.Predicate[] calldata itemPredicates
) external override whenNotPaused whenBorrowerReset {
»
    if (externalSigner != lender) revert OCM_SideMismatch(externalSigner);
```
However, checking that externalSigner is the lender address will revert for lenders that:
1. Are smart wallet addresses that validate signatures through ERC-1271.
2. Approve other addresses to create offers on their behalf using approve()
As such, borrowers cannot migrate their V3 loans using loan offers in V4 if the lender is either of the above.

## Recommendation
Consider validating lender signatures in migrateV3Loan() as such:
```diff
- (, address externalSigner) = _recoverSignature(newTerms, sig, sigProperties,
Side.LEND, itemPredicates);
+ (bytes32 sighash, address externalSigner) = _recoverSignature(newTerms, sig,
sigProperties, Side.LEND, itemPredicates);
// revert if the signer is not the lender
- if (externalSigner != lender) revert OCM_SideMismatch(externalSigner);
+ if (!isSelfOrApproved(lender, externalSigner) &&
!OriginationLibrary.isApprovedForContract(lender, sig, sighash)) {
+
revert OCM_SideMismatch(externalSigner);
+ }
```
Additionally, the externalSigner address should be passed to loanCore.consumeNonce(), instead of lender:
```diff
// consume v4 nonce
- loanCore.consumeNonce(lender, sigProperties.nonce, sigProperties.maxUses);
+ loanCore.consumeNonce(externalSigner, sigProperties.nonce, sigProperties.maxUses);
```
