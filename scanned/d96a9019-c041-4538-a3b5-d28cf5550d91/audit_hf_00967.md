# [M] Missing signingCounterparty in loanHash can lead to the signature being used with the wrong address

## Summary
Severity: Medium
Contest weight: 0.5867
Dataset id: 3030
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
loanHash is used in recoverTokenSignature and recoverItemsSignature to determine the external signer for a signature specifying only a collateral address and ID.
```solidity
bytes32 loanHash = keccak256(
    abi.encode(
        OriginationLibrary._TOKEN_ID_TYPEHASH,
        loanTerms.interestRate,
        loanTerms.durationSecs,
        loanTerms.collateralAddress,
        loanTerms.deadline,
        loanTerms.payableCurrency,
        loanTerms.principal,
        loanTerms.collateralId,
        loanTerms.affiliateCode,
        sigProperties.nonce,
        sigProperties.maxUses,
        uint8(side)
    )
);
```
However, it doesn't include the address of the signingCounterparty. Depending on the side, this could be the lender or the borrower address. This makes it possible for the recently disclosed ERC1271 bug to occur, where if a signer's smart wallet's isValidSignature() follows the reference implementation in ERC-1271, their signature can be used with the wrong address as the signingCounterparty. Consider the following example:
• Bob wants to be a lender with his smart wallet - he signs a signature with his EOA, which will return true when passed to his smart wallet's isValidSignature().
• Alice calls initializeLoan() with his signature but with his EOA as the lender address.
• isSelfOrApproved() in _validateCounterparties() passes since signer is Bob's EOA.
An important note is that the signature can't be replayed in this case, so the only impact is that it can be used with the wrong address.

## Recommendation
Include the signingCounterparty in the signature:
```solidity
function initializeLoan(
    LoanLibrary.LoanTerms calldata loanTerms,
    BorrowerData calldata borrowerData,
    address lender,
    Signature calldata sig,
    SigProperties calldata sigProperties,
    LoanLibrary.Predicate[] calldata itemPredicates
) public override returns (uint256 loanId) {
+
    address signingCounterparty = neededSide == Side.LEND ? lender : borrower;
+
    (bytes32 sighash, address externalSigner) = _recoverSignature(loanTerms, sig, sigProperties, signingCounterparty, neededSide, itemPredicates);
```
This stops the attack described above, as the signer and sighash would change if signingCounterparty were a different address. Hence, the signature check in _validateCounterparties() would fail.
