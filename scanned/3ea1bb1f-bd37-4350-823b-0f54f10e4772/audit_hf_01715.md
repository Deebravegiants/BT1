# [M] M-2 KintoWallet signatures underflow

## Summary
Severity: Medium
Contest weight: 0.4005
Dataset id: 9354
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
KintoWallet._validateSignatures has the following lines:  
```solidity
if (owners.length == 2) {
    (signatures[0], signatures[1]) =
        ByteSignature.extractTwoSignatures(userOp.signature);
} else {
    (signatures[0], signatures[1], signatures[2]) =
        ByteSignature.extractThreeSignatures(userOp.signature);
}
for (uint i = 0; i < owners.length; i++) {
    if (owners[i] == hash.recover(signatures[i])) {
        requiredSigners--;
    }
}
return requiredSigners;
```
• KintoWallet.sol#L220-L230  
Imagine we have 3 owners, and signerPolicy=2. It means that at least N-1 correct signatures are required = at least 2 signatures. Every correct signature found in the loop will decrease requiredSigners. If requiredSigners is equal to 0 in the end, it means the validation went correctly. But the third signature will make the underflow, and the whole validation will fail.

## Recommendation
Consider exiting the loop when requiredSigners reaches 0.
