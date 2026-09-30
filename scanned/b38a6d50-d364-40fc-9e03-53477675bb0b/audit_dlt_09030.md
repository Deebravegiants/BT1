# [?] Bug fix: use retries to manage logger/metrics race condition (#16647)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2023-04-03
Source: https://github.com/digital-asset/daml/commit/69d4a306005462da8e6063b4f86f2ef4bb1adbc4
Type: security-commit

## Details
Bug fix: use retries to manage logger/metrics race condition (#16647)

## Patch
### triggers/tests/src/test/scala/com/digitalasset/daml/lf/engine/trigger/TriggerRuleSimulationLib.scala
```diff
@@ -4,8 +4,8 @@
 package com.daml.lf.engine.trigger
 
 import akka.actor.ActorSystem
-import akka.stream.{FlowShape, KillSwitches, Materializer, SourceShape}
-import akka.stream.scaladsl.{Flow, GraphDSL, Keep, Sink, Source}
+import akka.stream.{FlowShape, KillSwitches, Materializer, RestartSettings, SourceShape}
+import akka.stream.scaladsl.{Flow, GraphDSL, Keep, RestartSource, Sink, Source}
 import com.daml.ledger.api.refinements.ApiTypes.{ApplicationId, Party}
 import com.daml.ledger.api.v1.command_submission_service.SubmitRequest
 import com.daml.ledger.api.v1.event.CreatedEvent
@@ -30,7 +30,7 @@ import org.scalacheck.Gen
 import java.util.UUID
 import scala.collection.mutable
 import scala.concurrent.{ExecutionContext, Future}
-import scala.concurrent.duration.{Duration, FiniteDuration}
+import scala.concurrent.duration._
 import scala.util.Try
 
 @SuppressWarnings(
@@ -66,7 +66,24 @@ private class TriggerRuleMetrics {
     metricTimingData = mutable.Map.empty
   }
 
-  def getMetrics: TriggerRuleMetrics.RuleMetrics = {
+  def getMetrics(
+      retries: Int = 5
+  )(implicit materializer: Materializer): Future[TriggerRuleMetrics.RuleMetrics] = {
+    val backoff = 50.milliseconds
+    val timeLimit = backoff * (1L to retries.toLong).sum
+    val restartSettings =
+      RestartSettings(minBackoff = backoff, maxBackoff = 1.second, randomFactor = 0.1)
+        .withMaxRestarts(retries, timeLimit)
+
+    RestartSource
+      .withBackoff(restartSettings) { () =>
+        Source.single(getMetrics)
+      }
+      .initialTimeout(timeLimit)
+      .runWith(Sink.head)
+  }
+
+  private[this] def getMetrics: TriggerRuleMetrics.RuleMetrics = {
     import TriggerRuleMetrics._
 
     require(
@@ -764,8 +781,8 @@ final class TriggerRuleSimulationLib private (
         val submissions = initStateSimulation.runWith(Sink.seq)
         val initState = initStateSimulation.toMat(Sink.ignore)(Keep.left).run()
 
-        submissions.map(_.map(_.value)).zip(initState).map { case (requests, state) =>
-          (requests, ruleMetrics.getMetrics, state)
+        submissions.map(_.map(_.value)).zip(initState).flatMap { case (requests, state) =>
+          ruleMetrics.getMetrics().map((requests, _, state))
         }
       }
     }
@@ -810,8 +827,8 @@ final class TriggerRuleSimulationLib private (
         val submissions = updateStateSimulation.runWith(Sink.seq)
         val nextState = updateStateSimulation.toMat(Sink.ignore)(Keep.left).run()
 
-        submissions.map(_.map(_.value)).zip(nextState).map { case (requests, state) =>
-          (requests, ruleMetrics.getMetrics, state)
+        submissions.map(_.map(_.value)).zip(nextState).flatMap { case (requests, state) =>
+          ruleMetrics.getMetrics().map((requests, _, state))
         }
       }
     }
```
