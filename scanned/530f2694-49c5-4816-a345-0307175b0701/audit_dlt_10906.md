# [?] NODE-2411 Avoid deadlock while closing BU stream (#3670)

## Summary
Severity: Unknown
Chain: Waves
Component: wavesplatform/Waves
Published: 2022-04-14
Source: https://github.com/wavesplatform/Waves/commit/eac3837f94f80fbad873ed46b098de4ca2fd3a3d
Type: security-commit

## Details
NODE-2411 Avoid deadlock while closing BU stream (#3670)

## Patch
### grpc-server/src/main/scala/com/wavesplatform/events/Repo.scala
```diff
@@ -1,7 +1,6 @@
 package com.wavesplatform.events
 
 import java.nio.{ByteBuffer, ByteOrder}
-
 import cats.syntax.semigroup._
 import com.google.common.primitives.Ints
 import com.wavesplatform.api.common.CommonBlocksApi
@@ -25,21 +24,19 @@ import monix.reactive.Observable
 import monix.reactive.subjects.PublishToOneSubject
 import org.iq80.leveldb.DB
 
+import java.util.concurrent.ConcurrentHashMap
 import scala.concurrent.Future
 import scala.util.Using
 import scala.util.control.Exception
 
-class Repo(db: DB, blocksApi: CommonBlocksApi)(implicit s: Scheduler)
-    extends BlockchainUpdatesApi
-    with BlockchainUpdateTriggers
-    with ScorexLogging {
+class Repo(db: DB, blocksApi: CommonBlocksApi)(implicit s: Scheduler) extends BlockchainUpdatesApi with BlockchainUpdateTriggers with ScorexLogging {
   private[this] val monitor     = new Object
   private[this] var liquidState = Option.empty[LiquidState]
-  private[this] var handlers    = Set.empty[Handler]
+  private[this] val handlers    = ConcurrentHashMap.newKeySet[Handler]()
 
   def shutdown(): Unit = monitor.synchronized {
     db.close()
-    handlers.foreach(_.shutdown())
+    handlers.forEach(_.shutdown())
   }
 
   def height: Int =
@@ -71,7 +68,7 @@ class Repo(db: DB, blocksApi: CommonBlocksApi)(implicit s: Scheduler)
 
     val ba = BlockAppended.from(block, diff, blockchainBeforeWithMinerReward)
     liquidState = Some(LiquidState(ba, Seq.empty))
-    handlers.foreach(_.handleUpdate(ba))
+    handlers.forEach(_.handleUpdate(ba))
   }
 
   override def onProcessMicroBlock(
@@ -90,7 +87,7 @@ class Repo(db: DB, blocksApi: CommonBlocksApi)(implicit s: Scheduler)
     val mba = MicroBlockAppended.from(microBlock, diff, blockchainBeforeWithMinerReward, totalBlockId, totalTransactionsRoot)
     liquidState = Some(ls.copy(microBlocks = ls.microBlocks :+ mba))
 
-    handlers.foreach(_.handleUpdate(mba))
+    handlers.forEach(_.handleUpdate(mba))
   }
 
   def rollbackData(toHeight: Int): Seq[BlockAppended] =
@@ -160,7 +157,7 @@ class Repo(db: DB, blocksApi: CommonBlocksApi)(implicit s: Scheduler)
 
     liquidState = None
 
-    handlers.foreach(_.rollbackBlock(microRollbacks, blockRollbacks))
+    handlers.forEach(_.rollbackBlock(microRollbacks, blockRollbacks))
   }
 
   override def onMicroBlockRollback(blockchainBefore: Blockchain, toBlockId: ByteStr): Unit = monitor.synchronized {
@@ -184,7 +181,7 @@ class Repo(db: DB, blocksApi: CommonBlocksApi)(implicit s: Scheduler)
             }
         }
 
-        handlers.foreach(
+        handlers.forEach(
           _.rollbackMicroBlock(
             MicroBlockRollbackCompleted(
               toBlockId,
@@ -225,12 +222,12 @@ class Repo(db: DB, blocksApi: CommonBlocksApi)(implicit s: Scheduler)
     monitor.synchronized {
       val subject = PublishToOneSubject[BlockchainUpdated]()
       val handler = new Handler(streamId, liquidState, subject, 250)
-      handlers += handler
+      handlers.add(handler)
 
-      val removeHandler = Task(monitor.synchronized {
+      val removeHandler = Task {
         log.info(s"[$streamId] Removing handler")
-        handlers -= handler
-      })
+        handlers.remove(handler)
+      }.void
 
       (new Loader(
         db,
```
