# [?] Fixed overflow issue with max duration (#975)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2019-04-30
Source: https://github.com/ACINQ/eclair/commit/de5a7827bd33cde1298cf1b64ec36d1f3325f4a7
Type: security-commit

## Details
Fixed overflow issue with max duration (#975)

This is a regression caused by #971, because `Duration` has a max value of `Long.MaxValue` *nanoseconds*, not *seconds*.

## Patch
### eclair-core/src/main/scala/fr/acinq/eclair/Eclair.scala
```diff
@@ -183,7 +183,7 @@ class EclairImpl(appKit: Kit) extends Eclair {
 
   override def audit(from_opt: Option[Long], to_opt: Option[Long])(implicit timeout: Timeout): Future[AuditResponse] = {
     val from = from_opt.getOrElse(0L)
-    val to = to_opt.getOrElse(Long.MaxValue)
+    val to = to_opt.getOrElse(MaxEpochSeconds)
 
     Future(AuditResponse(
       sent = appKit.nodeParams.db.audit.listSent(from, to),
@@ -194,7 +194,7 @@ class EclairImpl(appKit: Kit) extends Eclair {
 
   override def networkFees(from_opt: Option[Long], to_opt: Option[Long])(implicit timeout: Timeout): Future[Seq[NetworkFee]] = {
     val from = from_opt.getOrElse(0L)
-    val to = to_opt.getOrElse(Long.MaxValue)
+    val to = to_opt.getOrElse(MaxEpochSeconds)
 
     Future(appKit.nodeParams.db.audit.listNetworkFees(from, to))
   }
@@ -203,14 +203,14 @@ class EclairImpl(appKit: Kit) extends Eclair {
 
   override def allInvoices(from_opt: Option[Long], to_opt: Option[Long])(implicit timeout: Timeout): Future[Seq[PaymentRequest]] = Future {
     val from = from_opt.getOrElse(0L)
-    val to = to_opt.getOrElse(Long.MaxValue)
+    val to = to_opt.getOrElse(MaxEpochSeconds)
 
     appKit.nodeParams.db.payments.listPaymentRequests(from, to)
   }
 
   override def pendingInvoices(from_opt: Option[Long], to_opt: Option[Long])(implicit timeout: Timeout): Future[Seq[PaymentRequest]] = Future {
     val from = from_opt.getOrElse(0L)
-    val to = to_opt.getOrElse(Long.MaxValue)
+    val to = to_opt.getOrElse(MaxEpochSeconds)
 
     appKit.nodeParams.db.payments.listPendingPaymentRequests(from, to)
   }
```

### eclair-core/src/main/scala/fr/acinq/eclair/api/OldService.scala
```diff
@@ -41,8 +41,8 @@ import fr.acinq.eclair.io.{NodeURI, Peer}
 import fr.acinq.eclair.payment.PaymentLifecycle._
 import fr.acinq.eclair.payment._
 import fr.acinq.eclair.router.{ChannelDesc, RouteRequest, RouteResponse}
-import fr.acinq.eclair.wire.{ChannelAnnouncement, ChannelUpdate, NodeAddress, NodeAnnouncement}
-import fr.acinq.eclair.{AuditResponse, GetInfoResponse, Kit, ShortChannelId, feerateByte2Kw}
+import fr.acinq.eclair.wire.{ChannelAnnouncement, ChannelUpdate, NodeAnnouncement}
+import fr.acinq.eclair._
 import grizzled.slf4j.Logging
 import org.json4s.JsonAST.{JBool, JInt, JString}
 import org.json4s.{JValue, jackson}
@@ -316,7 +316,7 @@ trait OldService extends Logging {
                         case "audit" =>
                           val (from, to) = req.params match {
                             case JInt(from) :: JInt(to) :: Nil => (from.toLong, to.toLong)
-                            case _ => (0L, Long.MaxValue)
+                            case _ => (0L, MaxEpochSeconds)
                           }
                           completeRpcFuture(req.id, Future(AuditResponse(
                             sent = nodeParams.db.audit.listSent(from, to),
@@ -327,7 +327,7 @@ trait OldService extends Logging {
                         case "networkfees" =>
                           val (from, to) = req.params match {
                             case JInt(from) :: JInt(to) :: Nil => (from.toLong, to.toLong)
-                            case _ => (0L, Long.MaxValue)
+                            case _ => (0L, MaxEpochSeconds)
                           }
                           completeRpcFuture(req.id, Future(nodeParams.db.audit.listNetworkFees(from, to)))
 
```

### eclair-core/src/main/scala/fr/acinq/eclair/package.scala
```diff
@@ -23,6 +23,7 @@ import fr.acinq.bitcoin._
 import scodec.Attempt
 import scodec.bits.{BitVector, ByteVector}
 
+import scala.concurrent.duration.Duration
 import scala.util.{Failure, Success, Try}
 
 package object eclair {
@@ -70,7 +71,7 @@ package object eclair {
     */
   def feerateKw2Byte(feeratesPerKw: Long): Long = feeratesPerKw / 250
 
-  /*
+  /**
     why 253 and not 250 since feerate-per-kw is feerate-per-kb / 250 and the minimum relay fee rate is 1000 satoshi/Kb ?
 
     because bitcoin core uses neither the actual tx size in bytes or the tx weight to check fees, but a "virtual size"
@@ -82,13 +83,13 @@ package object eclair {
     with a conservative minimum weight of 400, we get a minimum feerate_per-kw of 253
 
     see https://github.com/ElementsProject/lightning/pull/1251
-   */
+   **/
   val MinimumFeeratePerKw = 253
 
-  /*
+  /**
     minimum relay fee rate, in satoshi per kilo
     bitcoin core uses virtual size and not the actual size in bytes, see above
-   */
+   **/
   val MinimumRelayFeeRate = 1000
 
   /**
@@ -151,4 +152,9 @@ package object eclair {
         }
     }
   }
+
+  /**
+    * We use this in the context of timestamp filtering, when we don't need an upper bound.
+    */
+  val MaxEpochSeconds = Duration.fromNanos(Long.MaxValue).toSeconds
 }
\ No newline at end of file
```
