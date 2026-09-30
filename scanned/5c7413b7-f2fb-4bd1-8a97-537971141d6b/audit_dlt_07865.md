# [?] avoid column quarantine crash with partial custody (#8491)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2026-05-22
Source: https://github.com/status-im/nimbus-eth2/commit/7e55a3da9a73b1f4e8821d0ba3207322b23f2930
Type: security-commit

## Details
avoid column quarantine crash with partial custody (#8491)

## Patch
### AllTests-mainnet.md
```diff
@@ -202,6 +202,7 @@ AllTests-mainnet
 + overfill protection test [node]                                                            OK
 + overfill test [node]                                                                       OK
 + overfill test [supernode]                                                                  OK
++ popSidecars tolerates partial custody at DA threshold [node]                               OK
 + pruneAfterFinalization() test [node]                                                       OK
 + put() duplicate items should not affect counters [node]                                    OK
 + put()/fetchMissingSidecars/remove test [node]                                              OK
@@ -786,6 +787,7 @@ AllTests-mainnet
 + overfill protection test [node]                                                            OK
 + overfill test [node]                                                                       OK
 + overfill test [supernode]                                                                  OK
++ popSidecars tolerates partial custody at DA threshold [node]                               OK
 + pruneAfterFinalization() test [node]                                                       OK
 + put() duplicate items should not affect counters [node]                                    OK
 + put()/fetchMissingSidecars/remove test [node]                                              OK
```

### beacon_chain/consensus_object_pools/column_quarantine.nim
```diff
@@ -528,14 +528,19 @@ proc popSidecars*[A: SomeDataColumnSidecar, B: OnDataColumnSidecarCallback](
             $sidecar.kind & "`")
         sidecars.add(sidecar.data)
   else:
+    let allowPartial = node[].value.count >= NUMBER_OF_COLUMNS div 2
     for cindex in quarantine.custodyMap:
-      let index = quarantine.getIndex(cindex)
-      doAssert(node[].value.sidecars[index].isLoaded(),
+      let sidecar = node[].value.sidecars[quarantine.getIndex(cindex)]
+      if allowPartial and sidecar.isEmpty():
+        continue
+      doAssert(sidecar.isLoaded(),
         "Record should only have loaded values, but it is `" &
-          $node[].value.sidecars[index].kind & "`")
-      sidecars.add(node[].value.sidecars[index].data)
+          $sidecar.kind & "`")
+      sidecars.add(sidecar.data)
 
-    doAssert(len(sidecars) == len(quarantine.custodyMap),
+    doAssert(
+      (allowPartial and len(sidecars) >= NUMBER_OF_COLUMNS div 2) or
+        len(sidecars) == len(quarantine.custodyMap),
       "Incorrect amount of sidecars in record for node - " & $len(sidecars))
 
   # popSidecars() should remove all the artifacts from the quarantine in both
```

### tests/test_quarantine.nim
```diff
@@ -454,6 +454,31 @@ suite "ColumnQuarantine data structure test suite " & preset():
     bq.remove(broot2)
     check len(bq) == 0
 
+  test "popSidecars tolerates partial custody at DA threshold [node]":
+    const custodyColumns =
+      (0 ..< (NUMBER_OF_COLUMNS div 2 + 32)).mapIt(it.ColumnIndex)
+    var bq = ColumnQuarantine.init(cfg, custodyColumns, quarantine, 0, nil)
+    let broot = genBlockRoot(1)
+
+    # Populate exactly half the column space — the DA threshold — at
+    # the first half of custody indices, leaving the rest of custody
+    # Empty.
+    var present: seq[ref fulu.DataColumnSidecar]
+    for i in 0 ..< (NUMBER_OF_COLUMNS div 2):
+      let sc = newClone(genFuluDataColumnSidecar(
+        index = int(custodyColumns[i]), slot = 1, proposer_index = 5))
+      bq.put(broot, sc)
+      present.add(sc)
+
+    check len(bq) == NUMBER_OF_COLUMNS div 2
+    let res = bq.popSidecars(broot)
+    check:
+      res.isOk()
+      # Populated subset is returned; Empty custody slots are silently
+      # skipped instead of crashing the node.
+      res.get().len == NUMBER_OF_COLUMNS div 2
+      compareSidecars(res.get(), present) == true
+
   test "put()/fetchMissingSidecars/remove test [node]":
     let
       custodyColumns =
@@ -2152,6 +2177,26 @@ suite "GloasColumnQuarantine data structure test suite " & preset():
     bq.remove(broot2)
     check len(bq) == 0
 
+  test "popSidecars tolerates partial custody at DA threshold [node]":
+    const custodyColumns =
+      (0 ..< (NUMBER_OF_COLUMNS div 2 + 32)).mapIt(it.ColumnIndex)
+    var bq = GloasColumnQuarantine.init(cfg, custodyColumns, quarantine, 0, nil)
+    let broot = genBlockRoot(1)
+
+    var present: seq[ref gloas.DataColumnSidecar]
+    for i in 0 ..< (NUMBER_OF_COLUMNS div 2):
+      let sc = newClone(genGloasDataColumnSidecar(
+        index = int(custodyColumns[i]), slot = 1))
+      bq.put(broot, sc)
+      present.add(sc)
+
+    check len(bq) == NUMBER_OF_COLUMNS div 2
+    let res = bq.popSidecars(broot)
+    check:
+      res.isOk()
+      res.get().len == NUMBER_OF_COLUMNS div 2
+      compareSidecars(res.get(), present) == true
+
   test "put()/fetchMissingSidecars/remove test [node]":
     let
       custodyColumns =
```
