# [H] Bypassing Multisig Execution Threshold with Duplicate Signatures

## Summary
Severity: High
Reporter: Atharv, KupiaSec, cergyk
Contest weight: 0.5949
Dataset id: 1877
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol implements a multisig mechanism requiring at least 2 out of 3 admin signatures (2/3) to execute a transaction. However, the implementation can be exploited by submitting duplicate signatures in the array, allowing a transaction to execute with only one admin's signature.
The code does not ensure uniqueness in the signatures array during validation. As a result, the loop increments the counter n for each signature, even if the same signature is repeated, allowing the require(n >= execN) check to pass incorrectly.
```solidity
for (uint i = 0; i < signatures.length; i++) {
    if (exec[recover(hash, signatures[i])]) {
        n++;
    }
}
require(n >= execN, "not enough signatures");
call function
```
And the call function is external hence anyone can call the function. Hence break the invarient that states it require atleast 2 admins to sign the payload to execute the transaction.
Internal pre-conditions
External pre-conditions
Attack Path
1. Transactions can be executed with fewer signatures than the required threshold, compromising the security guarantees of the multisig mechanism.
2. A single malicious or compromised admin can exploit this to execute unauthorized transactions.
3. The flaw entirely defeats the purpose of using multisig for enhanced transaction security.

## Recommendation
To fix this vulnerability, ensure that each element in the signatures array is unique
