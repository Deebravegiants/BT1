# [H] _validateCounterparties() incorrectly checks if sig belongs to the callingCounterparty

## Summary
Severity: High
Contest weight: 0.6412
Dataset id: 3015
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_validateCounterparties() validates that the caller is allowed to create a new loan for the lender and borrower addresses. This is done by checking that the caller is authorized create loans on the behalf of one party, known as the callingCounterparty, and the signature provided belongs to the other party, known as the signingCounterparty.

However, _validateCounterparties() incorrectly checks if the signature belongs to the callingCounterparty as such:

```solidity
if (!isSelfOrApproved(callingCounterparty, caller) &&
    !OriginationLibrary.isApprovedForContract(callingCounterparty, sig, sighash)) {
    revert OC_CallerNotParticipant(msg.sender);
}
```

The !OriginationLibrary.isApprovedForContract(callingCounterparty, sig, sighash) condition should not be there as the signature should belong to only the signingCounterparty, and not the callingCounterparty.

An attacker can abuse this to force a user with a Side.BORROW signature to become a lender:
- Assume Bob uses a smart contract wallet:
  - Bob's wallet has an existing approval of 1000 USDC to the LoanCore contract.
- Bob wants to borrow a loan using his Azuki NFT as collateral. He generates a signature with the following:
  - side = Side.BORROW
  - loanTerms.collateralAddress is the Azuki address
  - loanTerms.collateralId = 1337
  - loanTerms.payableCurrency is the USDC address
  - loanTerms.principal = 1000e6.
  Note that this amount can be anything smaller than Bob's approval.
- Alice wishes to make Bob become a lender for the loan, she does the following:
  - Deploy a malicious contract that will be the borrower address. Whenever isValidSignature() is called, its selector is always returned.
  - She buys Bob's Azuki NFT from him and transfers it to the malicious contract.
  - Before Bob can invalidate his signature using cancelNonce() in LoanCore, she calls initializeLoan() with the following arguments:
    * loanTerms is set to the terms in Bob's signature.
    * borrower is Alice's malicious contract.
    * lender is Bob's wallet.
    * sig is set to Bob's signature.
    * nonce is set to the nonce in Bob's signature.
  - Note that the caller (msg.sender) is Alice's address.
- In initializeLoan():
  - neededSide = Side.BORROW, as Alice's malicious contract is not approved by her address.
  - In _validateCounterparties():
    * signingCounterparty is Alice's malicious contract.
    * callingCounterparty is Bob's wallet.
    * The isApprovedForContract() check for callingCounterparty passes, as Bob is the signer of the BORROW signature.
    * The isApprovedForContract() check for signingCounterparty passes, as Alice's malicious contract returns the correct magic value for any signature.
- As a result, a new loan is created with Bob's wallet as the lender.

In the scenario above, Bob's signature was used to force him to become a lender, even though his signature contained Side.BORROW.

Note that the likelihood of a user having an existing approval to the LoanCore contract is not low; the user could be waiting for another loan to be created, where he is the lender that provides currency.

The exploit shown above can be used to manipulate signatures using any function that calls _validateCounterparties(), including:
- initializeLoan()
- initializeLoanWithItems()
- rolloverLoan()
- rolloverLoanWithItems()

## Recommendation
Remove the isApprovedForContract() condition for callingCounterparty:

```diff
if (!isSelfOrApproved(callingCounterparty, caller) &&
    !isApprovedForContract(callingCounterparty, sig, sighash)) {
+
    if (!isSelfOrApproved(callingCounterparty, caller)) {
    revert OC_CallerNotParticipant(msg.sender);
}
```
