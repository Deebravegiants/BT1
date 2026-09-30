# [?] Avoid overflow on empty multiproof (#4564)

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2023-09-04
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/a503ba1a0a1a5d1a434b6fca5e25ff5eca0a35fa
Type: security-commit

## Details
Avoid overflow on empty multiproof (#4564)

## Patch
### .changeset/large-humans-remain.md
```diff
@@ -0,0 +1,5 @@
+---
+'openzeppelin-solidity': patch
+---
+
+`MerkleProof`: Use custom error to report invalid multiproof instead of reverting with overflow panic.
```

### contracts/utils/cryptography/MerkleProof.sol
```diff
@@ -118,7 +118,7 @@ library MerkleProof {
         uint256 totalHashes = proofFlags.length;
 
         // Check proof validity.
-        if (leavesLen + proofLen - 1 != totalHashes) {
+        if (leavesLen + proofLen != totalHashes + 1) {
             revert MerkleProofInvalidMultiproof();
         }
 
@@ -174,7 +174,7 @@ library MerkleProof {
         uint256 totalHashes = proofFlags.length;
 
         // Check proof validity.
-        if (leavesLen + proofLen - 1 != totalHashes) {
+        if (leavesLen + proofLen != totalHashes + 1) {
             revert MerkleProofInvalidMultiproof();
         }
 
```
