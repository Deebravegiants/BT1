# [?] Fix out of bounds access if keepVersions is zero

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2022-02-07
Source: https://github.com/ergoplatform/ergo/commit/c4b4099b1ba09d25687d16e514f4a48e88fc400e
Type: security-commit

## Details
Fix out of bounds access if keepVersions is zero

refer #1600

## Patch
### avldb/benchmarks/src/main/scala/scorex/crypto/authds/benchmarks/Helper.scala
```diff
@@ -33,11 +33,11 @@ object Helper {
     inserts ++ updates
   }
 
-  def persistentProverWithVersionedStore(keepVersions: Int,
+  def persistentProverWithVersionedStore(initialKeepVersions: Int,
                                          baseOperationsCount: Int = 0): (Prover, LDBVersionedStore, VersionedLDBAVLStorage[Digest32]) = {
     val dir = java.nio.file.Files.createTempDirectory("bench_testing_" + scala.util.Random.alphanumeric.take(15)).toFile
     dir.deleteOnExit()
-    val store = new LDBVersionedStore(dir, initialKeepVersions = keepVersions)
+    val store = new LDBVersionedStore(dir, initialKeepVersions = initialKeepVersions)
     val storage = new VersionedLDBAVLStorage(store, NodeParameters(kl, Some(vl), ll))
     require(storage.isEmpty)
     val prover = new BatchAVLProver[Digest32, HF](kl, Some(vl))
```

### avldb/src/main/scala/scorex/db/LDBVersionedStore.scala
```diff
@@ -270,7 +270,11 @@ class LDBVersionedStore(protected val dir: File, val initialKeepVersions: Int) e
     val deteriorated = versions.size - count
     if (deteriorated > 0) {
       val fromLsn = versionLsn(0)
-      val tillLsn = versionLsn(deteriorated)
+      val tillLsn = if (count > 0) {
+        versionLsn(deteriorated)
+      } else {
+        versionLsn.last + 1 /* exclusive boundary */
+      }
       val batch = undo.createWriteBatch()
       try {
         for (lsn <- fromLsn until tillLsn) {
```

### avldb/src/test/scala/scorex/crypto/authds/avltree/batch/helpers/TestHelper.scala
```diff
@@ -23,9 +23,9 @@ trait TestHelper extends FileHelper {
 
   implicit val hf: HF = Blake2b256
 
-  def createVersionedStore(keepVersions: Int = 10): LDBVersionedStore = {
+  def createVersionedStore(initialKeepVersions: Int = 10): LDBVersionedStore = {
     val dir = getRandomTempDir
-    new LDBVersionedStore(dir, initialKeepVersions = keepVersions)
+    new LDBVersionedStore(dir, initialKeepVersions = initialKeepVersions)
   }
 
   def createVersionedStorage(store: LDBVersionedStore): STORAGE =
```

### avldb/src/test/scala/scorex/db/LDBVersionedStoreSpec.scala
```diff
@@ -96,5 +96,6 @@ class LDBVersionedStoreSpec extends AnyPropSpec with Matchers {
     store.versionIdExists(version1) shouldBe false
     store.versionIdExists(version2) shouldBe true
     store.setKeepVersions(10) shouldBe 1
+    store.setKeepVersions(0) shouldBe 10
   }
 }
```
