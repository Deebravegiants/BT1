# [M] In some cases a signatures nonce maxUses can be violated.

## Summary
Severity: Medium
Contest weight: 0.4500
Dataset id: 3012
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In a signature, the signer specifies a maxUses value representing how many times a signature can be used.

The LoanCore._useNonce() function will mark a nonce as “used” when it has been used maxUses times.

```solidity
function _useNonce(address user, uint160 nonce, uint96 maxUses) internal {
    // load nonce data
    mapping(uint160 => bool) storage _usedNonces = usedNonces[user];
    uint96 _nonceUses = numNonceUses[user][nonce];
    // check if nonce has been completely used or cancelled
    if (_usedNonces[nonce]) revert LC_NonceUsed(user, nonce);
    if (_nonceUses + 1 == maxUses) {
        // if this is the last time nonce can be used, mark the nonce as completely used
        // and update the number of times it has been used to the maxUses
        _usedNonces[nonce] = true;
        numNonceUses[user][nonce] = maxUses;
        emit NonceUsed(user, nonce);
    } else {
        // if this nonce usage is not the last use and is not over the maxUses,
        // increment the numNonceUses mapping
        numNonceUses[user][nonce]++;
    }
}
```

However, if maxUses <= _nonceUses, the signature can be used infinitely as _nonceUses + 1 == maxUses will never be true.

This could occur if:
1. The user creates a signature with maxUses = 0
2. The user re-uses a nonce that was used in an old signature that didn't reach maxUses

Another example would be:
- The user creates a signature with nonce = 1 and maxUses = 5
- The signature is used 4 times
- The user signs a new signature with nonce = 1 and maxUses = 2
- Since _nonceUses = 4 and maxUses will always be smaller than _nonceUses + 1, the second signature can be used infinitely many times.

## Recommendation
Consider reverting when maxUses is not greater than nonceUses:

```diff
@@ -883,7 +883,7 @@ contract LoanCore is
    uint96 _nonceUses = numNonceUses[user][nonce];
    // check if nonce has been completely used or cancelled
    if (_usedNonces[nonce]) revert LC_NonceUsed(user, nonce);
+
    if (_usedNonces[nonce] || maxUses <= _nonceUses) revert LC_NonceUsed(user, nonce);
    if (_nonceUses + 1 == maxUses) {
```
