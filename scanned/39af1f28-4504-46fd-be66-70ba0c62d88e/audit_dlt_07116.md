# [?] annotate slashing protection v2 with uint64 -> int64 overflow conditions (#2392)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2021-03-10
Source: https://github.com/status-im/nimbus-eth2/commit/82c300186be55048d30fc69479c17839ebeec27a
Type: security-commit

## Details
annotate slashing protection v2 with uint64 -> int64 overflow conditions (#2392)

* annotate slashing protection v2 with uint64 -> int64 overflow conditions

* fix variables

* remove assertion which gets tripped by interchange tests

## Patch
### beacon_chain/validators/slashing_protection_v2.nim
```diff
@@ -720,6 +720,11 @@ proc checkSlashableBlockProposal*(
   block:
     # Condition 1 at https://eips.ethereum.org/EIPS/eip-3076
     var root: ETH2Digest
+
+    # 6 second (minimal preset) slots => overflow at ~1.75 trillion years under
+    # minimal preset, and twice that with mainnet preset
+    doAssert slot <= high(int64).uint64
+
     let status = db.sqlBlockForSameSlot.exec(
           (valID, int64 slot)
         ) do (res: Hash32):
@@ -758,6 +763,10 @@ proc checkSlashableBlockProposal*(
     let status = db.sqlBlockMinSlot.exec(valID) do (res: int64):
       minSlot = res
     if status.foundAnyResult():
+      # 6 second (minimal preset) slots => overflow at ~1.75 trillion years
+      # under minimal preset, and twice that under mainnet preset
+      doAssert slot <= high(int64).uint64
+
       if int64(slot) <= minSlot:
         return err(BadProposal(
           kind: MinSlotViolation,
@@ -805,6 +814,10 @@ proc checkSlashableAttestation*(
   block:
     # Condition 3 part 1/3 at https://eips.ethereum.org/EIPS/eip-3076
     var root: ETH2Digest
+
+    # Overflows in 14 trillion years (minimal) or 112 trillion years (mainnet)
+    doAssert target <= high(int64).uint64
+
     let status = db.sqlAttForSameTargetEpoch.exec(
           (valID, int64 target)
         ) do (res: Hash32):
@@ -826,6 +839,11 @@ proc checkSlashableAttestation*(
     # Condition 3 part 2/3 at https://eips.ethereum.org/EIPS/eip-3076
     var root: ETH2Digest
     var db_source, db_target: Epoch
+
+    # Overflows in 14 trillion years (minimal) or 112 trillion years (mainnet)
+    doAssert source <= high(int64).uint64
+    doAssert target <= high(int64).uint64
+
     let status = db.sqlAttSurrounded.exec(
           (valID, int64 source, int64 target)
         ) do (res: tuple[source, target: int64, root: Hash32]):
@@ -893,13 +911,19 @@ proc checkSlashableAttestation*(
       minTargetEpoch = res.target
 
     if status.foundAnyResult():
+      # Overflows in 14 trillion years (minimal) or 112 trillion years (mainnet)
+      doAssert source <= high(int64).uint64
+
       if source.int64 < minSourceEpoch:
         return err(BadVote(
           kind: MinSourceViolation,
           minSource: Epoch minSourceEpoch,
           candidateSource: source
         ))
 
+      # Overflows in 14 trillion years (minimal) or 112 trillion years (mainnet)
+      doAssert target <= high(int64).uint64
+
       if target.int64 <= minTargetEpoch:
         return err(BadVote(
           kind: MinTargetViolation,
@@ -945,6 +969,11 @@ proc registerBlock*(
   ## `checkSlashableBlockProposal` MUST be run
   ## before to ensure no overwrite.
   let valID = db.getOrRegisterValidator(validator)
+
+  # 6 second (minimal preset) slots => overflow at ~1.75 trillion years under
+  # minimal preset, and twice that with mainnet preset
+  doAssert slot <= high(int64).uint64
+
   let status = db.sqlInsertBlock.exec(
     (valID, int64 slot,
     block_root.data))
@@ -961,6 +990,11 @@ proc registerAttestation*(
   ## `checkSlashableAttestation` MUST be run
   ## before to ensure no overwrite.
   let valID = db.getOrRegisterValidator(validator)
+
+  # Overflows in 14 trillion years (minimal) or 112 trillion years (mainnet)
+  doAssert source <= high(int64).uint64
+  doAssert target <= high(int64).uint64
+
   let status = db.sqlInsertAtt.exec(
     (valID, int64 source, int64 target,
     attestation_root.data))
@@ -991,6 +1025,7 @@ proc pruneAttestations*(
   ## Prune all blocks from a validator before the specified newMinSlot
   ## This is intended for interchange import.
   let valID = db.getOrRegisterValidator(validator)
+
   let status = db.sqlPruneValidatorAttestations.exec(
     (valID, int64 newMinSourceEpoch, int64 newMinTargetEpoch))
   doAssert status.isOk(),
```
