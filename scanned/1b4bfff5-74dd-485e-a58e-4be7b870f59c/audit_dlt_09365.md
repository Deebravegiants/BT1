# [?] fix: HA deadlock for last block edge case (#21690)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-03-17
Source: https://github.com/AztecProtocol/aztec-packages/commit/f503d617c7b9f032bcba4b40e56fa5d033dd8541
Type: security-commit

## Details
fix: HA deadlock for last block edge case (#21690)

change ordering for `lastBlock` case when creating a checkpoint
proposal, so that we first sign the last block and then the checkpoint

## Patch
### yarn-project/stdlib/src/p2p/checkpoint_proposal.ts
```diff
@@ -178,29 +178,32 @@ export class CheckpointProposal extends Gossipable {
       blockNumber: lastBlockInfo?.blockHeader?.globalVariables.blockNumber ?? BlockNumber(0),
       dutyType: DutyType.CHECKPOINT_PROPOSAL,
     };
-    const checkpointSignature = await payloadSigner(checkpointHash, checkpointContext);
 
-    if (!lastBlockInfo) {
-      return new CheckpointProposal(checkpointHeader, archiveRoot, feeAssetPriceModifier, checkpointSignature);
+    if (lastBlockInfo) {
+      // Sign block proposal before signing checkpoint proposal to ensure HA protection
+      const lastBlockProposal = await BlockProposal.createProposalFromSigner(
+        lastBlockInfo.blockHeader,
+        lastBlockInfo.indexWithinCheckpoint,
+        checkpointHeader.inHash,
+        archiveRoot,
+        lastBlockInfo.txHashes,
+        lastBlockInfo.txs,
+        payloadSigner,
+      );
+
+      const checkpointSignature = await payloadSigner(checkpointHash, checkpointContext);
+
+      return new CheckpointProposal(checkpointHeader, archiveRoot, feeAssetPriceModifier, checkpointSignature, {
+        blockHeader: lastBlockInfo.blockHeader,
+        indexWithinCheckpoint: lastBlockInfo.indexWithinCheckpoint,
+        txHashes: lastBlockInfo.txHashes,
+        signature: lastBlockProposal.signature,
+        signedTxs: lastBlockProposal.signedTxs,
+      });
     }
 
-    const lastBlockProposal = await BlockProposal.createProposalFromSigner(
-      lastBlockInfo.blockHeader,
-      lastBlockInfo.indexWithinCheckpoint,
-      checkpointHeader.inHash,
-      archiveRoot,
-      lastBlockInfo.txHashes,
-      lastBlockInfo.txs,
-      payloadSigner,
-    );
-
-    return new CheckpointProposal(checkpointHeader, archiveRoot, feeAssetPriceModifier, checkpointSignature, {
-      blockHeader: lastBlockInfo.blockHeader,
-      indexWithinCheckpoint: lastBlockInfo.indexWithinCheckpoint,
-      txHashes: lastBlockInfo.txHashes,
-      signature: lastBlockProposal.signature,
-      signedTxs: lastBlockProposal.signedTxs,
-    });
+    const checkpointSignature = await payloadSigner(checkpointHash, checkpointContext);
+    return new CheckpointProposal(checkpointHeader, archiveRoot, feeAssetPriceModifier, checkpointSignature);
   }
 
   /**
```
