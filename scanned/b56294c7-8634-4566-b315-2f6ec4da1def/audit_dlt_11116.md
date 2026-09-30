# [?] Merge pull request #1671 from matter-labs/fix-fungible-token-overflow

## Summary
Severity: Unknown
Chain: zkSync Lite
Component: matter-labs/zksync
Published: 2021-06-02
Source: https://github.com/matter-labs/zksync/commit/f44b6bca5f373f2073790669f7ffa96a343a65b7
Type: security-commit

## Details
Merge pull request #1671 from matter-labs/fix-fungible-token-overflow

audit: fix fungible token overflow

## Patch
### contracts/contracts/ZkSync.sol
```diff
@@ -497,9 +497,13 @@ contract ZkSync is UpgradeableMaster, Storage, Config, Events, ReentrancyGuard {
 
             if (opType == Operations.OpType.PartialExit) {
                 Operations.PartialExit memory op = Operations.readPartialExitPubdata(pubData);
+
+                require(op.tokenId <= MAX_FUNGIBLE_TOKEN_ID, "mf1");
                 withdrawOrStore(uint16(op.tokenId), op.owner, op.amount);
             } else if (opType == Operations.OpType.ForcedExit) {
                 Operations.ForcedExit memory op = Operations.readForcedExitPubdata(pubData);
+
+                require(op.tokenId <= MAX_FUNGIBLE_TOKEN_ID, "mf2");
                 withdrawOrStore(uint16(op.tokenId), op.target, op.amount);
             } else if (opType == Operations.OpType.FullExit) {
                 Operations.FullExit memory op = Operations.readFullExitPubdata(pubData);
```
