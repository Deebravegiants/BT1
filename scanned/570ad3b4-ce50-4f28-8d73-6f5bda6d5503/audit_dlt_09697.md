# [?] close #1067: crash on MacOs

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2020-10-02
Source: https://github.com/ergoplatform/ergo/commit/2c57284faa3eb6348c21f150f567bd982d47caa1
Type: security-commit

## Details
close #1067: crash on MacOs

## Patch
### avldb/src/main/scala/scorex/db/LDBFactory.scala
```diff
@@ -2,8 +2,7 @@ package scorex.db
 
 import java.io.File
 import java.util.concurrent.locks.ReentrantReadWriteLock
-
-import org.iq80.leveldb.{DB, Range, DBFactory, DBIterator, Options, ReadOptions, Snapshot, WriteBatch, WriteOptions}
+import org.iq80.leveldb.{DB, DBFactory, DBIterator, Options, Range, ReadOptions, Snapshot, WriteBatch, WriteOptions}
 import scorex.util.ScorexLogging
 
 import scala.collection.mutable
@@ -138,15 +137,25 @@ object LDBFactory extends ScorexLogging {
 
   lazy val factory: DBFactory = {
     val loaders = List(ClassLoader.getSystemClassLoader, this.getClass.getClassLoader)
-    val factories = List(nativeFactory, javaFactory)
+
+    // As LevelDB-JNI has problems on Mac (see https://github.com/ergoplatform/ergo/issues/1067),
+    // we are using only pure-Java LevelDB on Mac
+    val isMac = System.getProperty("os.name").toLowerCase().indexOf("mac") >= 0
+    val factories = if(isMac) {
+      List(javaFactory)
+    } else {
+      List(nativeFactory, javaFactory)
+    }
+
     val pairs = loaders.view
       .zip(factories)
       .flatMap { case (loader, factoryName) =>
         loadFactory(loader, factoryName).map(factoryName -> _)
       }
 
-    val (name, factory) = pairs.headOption.getOrElse(
-      throw new RuntimeException(s"Could not load any of the factory classes: $nativeFactory, $javaFactory"))
+    val (name, factory) = pairs.headOption.getOrElse {
+      throw new RuntimeException(s"Could not load any of the factory classes: $factories")
+    }
 
     if (name == javaFactory) {
       log.warn("Using the pure java LevelDB implementation which is still experimental")
```
