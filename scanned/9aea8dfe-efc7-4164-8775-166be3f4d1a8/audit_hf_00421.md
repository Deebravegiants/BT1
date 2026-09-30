# [M] Signer can avoid restrictions and

## Summary
Severity: Medium
Contest weight: 0.4609
Dataset id: 1832
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In order to make sure that a delegatecall does not change Safe's state, HSG's checkTransaction stores the current threshold, owners list and fallback handler. Then, after the call is executed, checkAfterExecution is supposed to verify that these variables have not been changed.  
```solidity
if (operation == Enum.Operation.DelegateCall) {
    // case: DELEGATECALL
    // We disallow delegatecalls to unapproved targets
    // Otherwise record the existing owners and threshold for post-flight checks to ensure that Safe state has not
    // been altered
    _existingOwnersHash = keccak256(abi.encode(owners));
    _existingThreshold = threshold;
    _existingFallbackHandler = safe.getSafeFallbackHandler();
```
However, since the checkTransaction can be re-entered by a new call, these restrictions can easily be bypassed. If the delegatecall changes the owners and the threshold, the executing signer can then just provide a new transaction to be executed with the new owners being just him and threshold set to 1. This will then override the above stored variables. Because of this the checkAfterExecution check will also succeed.  
Possible reentrancy within checkTransaction  
Attack Path  
1. Signers sign a tx which would alter the owners list and set the threshold to 1.  
2. Within that delegatecall, the only remaining owner signs a new transaction and executes it. It doesn't realistically matter what the tx is.  
3. checkTransaction is entered. _existingOwnersHash and _existingThreshold are overwritten to their new values.  
4. The checkAfterExecution on both the inner and the outer call check against the altered values, hence they both succeed.  
5. In the end, the intended restrictions are bypassed and the ownerlist and threshold are both overwritten.  
6. The user who has remained the only owner has full access over the multi-sig until the other owners re-claim their hats.  
Users can bypassed intended restrictions not to be able to overwrite the owner list and threshold variables.

## Recommendation
If checkTransaction is entered, and the transient variables have already been assigned values, revert if the values differ from the current ones.
