# [?] Fixing SignedNodeInfoe security issue (#2908)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2018-04-03
Source: https://github.com/corda/corda/commit/2f1b8ff23e5a0400f72ff603da10b849604c6b04
Type: security-commit

## Details
Fixing SignedNodeInfoe security issue (#2908)

## Patch
### node-api/src/main/kotlin/net/corda/nodeapi/internal/SignedNodeInfo.kt
```diff
@@ -25,7 +25,7 @@ class SignedNodeInfo(val raw: SerializedBytes<NodeInfo>, val signatures: List<Di
     fun verified(): NodeInfo {
         val nodeInfo = raw.deserialize()
         val identities = nodeInfo.legalIdentities.filterNot { it.owningKey is CompositeKey }
-
+        require(identities.isNotEmpty()) { "At least one identity with a non-composite key needs to be specified." }
         if (identities.size < signatures.size) {
             throw SignatureException("Extra signatures. Found ${signatures.size} expected ${identities.size}")
         }
```
