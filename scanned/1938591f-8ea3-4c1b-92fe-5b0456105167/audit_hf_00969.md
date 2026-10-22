# [M] The borrowers callbackData is not included in signatures

## Summary
Severity: Medium
Contest weight: 0.5977
Dataset id: 3032
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When initializing a loan, the callee can assign callbackData to the borrowerData to execute an operation once the loan is initialized.
```solidity
function initializeLoan(
    LoanLibrary.LoanTerms calldata loanTerms,
    BorrowerData calldata borrowerData,
    address lender,
    Signature calldata sig,
    SigProperties calldata sigProperties,
    LoanLibrary.Predicate[] calldata itemPredicates
) public override returns (uint256 loanId) {
    Side neededSide = isSelfOrApproved(borrowerData.borrower, msg.sender) ?
    Side.LEND : Side.BORROW;
    (bytes32 sighash, address externalSigner) = _recoverSignature(loanTerms, sig,
    sigProperties, neededSide, itemPredicates);
    loanCore.consumeNonce(externalSigner, sigProperties.nonce,
    sigProperties.maxUses);
>
    loanId = _initialize(loanTerms, borrowerData, lender);

function _initialize(
    LoanLibrary.LoanTerms calldata loanTerms,
    BorrowerData calldata borrowerData,
    address lender
) internal nonReentrant returns (uint256 loanId) {
    if (borrowerData.callbackData.length > 0) {
>
        IExpressBorrow(borrowerData.borrower).executeOperation(msg.sender,
        lender, loanTerms, borrowerFee, borrowerData.callbackData);
}
```
However, it can be observed that borrowerData.callbackData isn't included in the signature » (bytes32 sighash, address externalSigner) = _recoverSignature(loanTerms, sig, sigProperties, neededSide, itemPredicates); This becomes an issue when neededSide is Side.BORROW since the caller is the lender - the caller can modify borrowerData.callbackData or pass empty bytes, and the call would still pass. If the borrower's executeOperation() callback uses callbackData, it could function differently than expected. Hence, the signature should include the callback data here so the counterparty can know if the callback will be executed.

## Recommendation
Include borrowerData.callbackData in the signature:
```solidity
function initializeLoan(
    LoanLibrary.LoanTerms calldata loanTerms,
    BorrowerData calldata borrowerData,
    address lender,
    Signature calldata sig,
    SigProperties calldata sigProperties,
    LoanLibrary.Predicate[] calldata itemPredicates
) public override returns (uint256 loanId) {
    (bytes32 sighash, address externalSigner) = _recoverSignature(loanTerms, sig,
    sigProperties, neededSide, itemPredicates);
+
    (bytes32 sighash, address externalSigner) = _recoverSignature(loanTerms, sig,
    sigProperties, neededSide, itemPredicates, borrowerData.callbackData);
    loanCore.consumeNonce(externalSigner, sigProperties.nonce,
    sigProperties.maxUses);
    loanId = _initialize(loanTerms, borrowerData, lender);
```
