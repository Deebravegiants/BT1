# [?] Fixed stack overflow in data iterator (#3927)

## Summary
Severity: Unknown
Chain: Waves
Component: wavesplatform/Waves
Published: 2023-12-11
Source: https://github.com/wavesplatform/Waves/commit/bb5cb6d7598e87f0a7dcadae437b470d66bbf767
Type: security-commit

## Details
Fixed stack overflow in data iterator (#3927)

## Patch
### node/src/main/scala/com/wavesplatform/api/common/CommonAccountsApi.scala
```diff
@@ -14,8 +14,10 @@ import com.wavesplatform.state.{AccountScriptInfo, AssetDescription, Blockchain,
 import com.wavesplatform.transaction.Asset.IssuedAsset
 import monix.eval.Task
 import monix.reactive.Observable
+import org.rocksdb.RocksIterator
 
 import java.util.regex.Pattern
+import scala.annotation.tailrec
 import scala.jdk.CollectionConverters.*
 
 trait CommonAccountsApi {
@@ -134,18 +136,19 @@ object CommonAccountsApi {
       entriesFromDiff: Array[DataEntry[?]],
       pattern: Option[Pattern]
   ) extends AbstractIterator[DataEntry[?]] {
-    val prefix: Array[Byte] = KeyTags.Data.prefixBytes ++ PBRecipients.publicKeyHash(address)
+    private val prefix: Array[Byte] = KeyTags.Data.prefixBytes ++ PBRecipients.publicKeyHash(address)
 
-    val length: Int = entriesFromDiff.length
+    private val length: Int = entriesFromDiff.length
 
     db.withSafePrefixIterator(_.seek(prefix))()
 
-    var nextIndex                         = 0
-    var nextDbEntry: Option[DataEntry[?]] = None
+    private var nextIndex                         = 0
+    private var nextDbEntry: Option[DataEntry[?]] = None
 
-    def matches(key: String): Boolean = pattern.forall(_.matcher(key).matches())
+    private def matches(key: String): Boolean = pattern.forall(_.matcher(key).matches())
 
-    final override def computeNext(): DataEntry[?] = db.withSafePrefixIterator { dbIterator =>
+    @tailrec
+    private def doComputeNext(iter: RocksIterator): DataEntry[?] =
       nextDbEntry match {
         case Some(dbEntry) =>
           if (nextIndex < length) {
@@ -166,22 +169,26 @@ object CommonAccountsApi {
             dbEntry
           }
         case None =>
-          if (dbIterator.isValid) {
-            val key = new String(dbIterator.key().drop(2 + Address.HashLength), Charsets.UTF_8)
+          if (!iter.isValid) {
+            if (nextIndex < length) {
+              nextIndex += 1
+              entriesFromDiff(nextIndex - 1)
+            } else {
+              endOfData()
+            }
+          } else {
+            val key = new String(iter.key().drop(2 + Address.HashLength), Charsets.UTF_8)
             if (matches(key)) {
-              nextDbEntry = Option(dbIterator.value()).map { arr =>
+              nextDbEntry = Option(iter.value()).map { arr =>
                 Keys.data(address, key).parse(arr).entry
               }
             }
-            dbIterator.next()
-            computeNext()
-          } else if (nextIndex < length) {
-            nextIndex += 1
-            entriesFromDiff(nextIndex - 1)
-          } else {
-            endOfData()
+            iter.next()
+            doComputeNext(iter)
           }
       }
-    }(endOfData())
+
+    override def computeNext(): DataEntry[?] =
+      db.withSafePrefixIterator(doComputeNext)(endOfData())
   }
 }
```

### node/src/test/scala/com/wavesplatform/http/AddressRouteSpec.scala
```diff
@@ -3,54 +3,45 @@ package com.wavesplatform.http
 import akka.http.scaladsl.model.*
 import akka.http.scaladsl.model.HttpEntity.{Chunk, LastChunk}
 import akka.http.scaladsl.model.headers.{Accept, `Content-Type`, `Transfer-Encoding`}
-import akka.http.scaladsl.testkit.RouteTestTimeout
 import akka.stream.scaladsl.Source
 import com.google.common.primitives.Longs
-import com.google.protobuf.ByteString
-import com.wavesplatform.account.Address
-import com.wavesplatform.api.common.CommonAccountsApi
 import com.wavesplatform.api.http.ApiError.{ApiKeyNotValid, DataKeysNotSpecified, TooBigArrayAllocation}
 import com.wavesplatform.api.http.{AddressApiRoute, RouteTimeout}
 import com.wavesplatform.common.state.ByteStr
-import com.wavesplatform.common.utils.{Base58, EitherExt2}
-import com.wavesplatform.db.WithDomain
+import com.wavesplatform.common.utils.Base58
+import com.wavesplatform.db.WithState
 import com.wavesplatform.db.WithState.AddrWithBalance
 import com.wavesplatform.features.BlockchainFeatures
-import com.wavesplatform.lang.contract.DApp
-import com.wavesplatform.lang.contract.DApp.{CallableAnnotation, CallableFunction, VerifierAnnotation, VerifierFunction}
-import com.wavesplatform.lang.directives.values.V3
-import com.wavesplatform.lang.script.ContractScript
-import com.wavesplatform.lang.script.v1.ExprScript
-import com.wavesplatform.lang.v1.compiler.Terms.*
+import com.wavesplatform.lang.directives.values.{V5, V6}
+import com.wavesplatform.lang.v1.compiler.TestCompiler
 import com.wavesplatform.protobuf.dapp.DAppMeta
-import com.wavesplatform.protobuf.dapp.DAppMeta.CallableFuncSignature
-import com.wavesplatform.settings.WalletSettings
+import com.wavesplatform.settings.{WalletSettings, WavesSettings}
+import com.wavesplatform.state.IntegerDataEntry
 import com.wavesplatform.state.diffs.FeeValidation
-import com.wavesplatform.state.{AccountScriptInfo, Blockchain}
 import com.wavesplatform.test.*
 import com.wavesplatform.transaction.TxHelpers
 import com.wavesplatform.utils.{Schedulers, SharedSchedulerMixin}
 import com.wavesplatform.wallet.Wallet
 import io.netty.util.HashedWheelTimer
 import monix.execution.schedulers.SchedulerService
-import org.scalamock.scalatest.PathMockFactory
 import play.api.libs.json.*
 import play.api.libs.json.Json.JsValueWrapper
 
 import scala.concurrent.duration.*
 
-class AddressRouteSpec extends RouteSpec("/addresses") with PathMockFactory with RestAPISettingsHelper with WithDomain with SharedSchedulerMixin {
+class AddressRouteSpec extends RouteSpec("/addresses") with RestAPISettingsHelper with SharedDomain with SharedSchedulerMixin {
+
+  private val richAccount = TxHelpers.signer(0xaaff)
+
+  override def settings: WavesSettings                         = DomainPresets.RideV6.copy(restAPISettings = restAPISettings)
+  override def genesisBalances: Seq[WithState.AddrWithBalance] = Seq(AddrWithBalance(richAccount.toAddress, 10_000.waves))
 
   private val wallet = Wallet(WalletSettings(None, Some("123"), Some(ByteStr(Longs.toByteArray(System.nanoTime())))))
   wallet.generateNewAccounts(10)
   private val allAccounts  = wallet.privateKeyAccounts
   private val allAddresses = allAccounts.map(_.toAddress)
-  private val blockchain   = stub[Blockchain]("globalBlockchain")
-  (() => blockchain.activatedFeatures).when().returning(Map())
-
-  private[this] val utxPoolSynchronizer = DummyTransactionPublisher.accepting
 
-  private val commonAccountApi = mock[CommonAccountsApi]("globalAccountApi")
+  private val utxPoolSynchronizer = DummyTransactionPublisher.accepting
 
   private val timeLimited: SchedulerService = Schedulers.timeBoundedFixedPool(
     new HashedWheelTimer(),
@@ -63,83 +54,70 @@ class AddressRouteSpec extends RouteSpec("/addresses") with PathMockFactory with
     timeLimited.shutdown()
     super.afterAll()
   }
-  private val addressApiRoute: AddressApiRoute = AddressApiRoute(
-    restAPISettings,
-    wallet,
-    blockchain,
-    utxPoolSynchronizer,
-    new TestTime,
-    timeLimited,
-    new RouteTimeout(60.seconds)(sharedScheduler),
-    commonAccountApi,
-    5
+
+  private val MaxBalanceDepth = 5
+
+  private val route = seal(
+    AddressApiRoute(
+      restAPISettings,
+      wallet,
+      domain.blockchain,
+      utxPoolSynchronizer,
+      new TestTime,
+      timeLimited,
+      new RouteTimeout(60.seconds)(sharedScheduler),
+      domain.accountsApi,
+      MaxBalanceDepth
+    ).route
   )
-  private val route = seal(addressApiRoute.route)
-
-  routePath("/balance/{address}/{confirmations}") in withDomain(balances = Seq(AddrWithBalance(TxHelpers.defaultAddress))) { d =>
-    val route =
-      addressApiRoute
-        .copy(
-          blockchain = d.blockchainUpdater,
-          commonAccountsApi = CommonAccountsApi(
-            () => d.blockchainUpdater.snapshotBlockchain,
-            d.rdb,
-            d.blockchainUpdater
-          )
-        )
-        .route
+
+  routePath("/balance/{address}/{confirmations}") in {
     val address = TxHelpers.signer(1).toAddress
 
-    for (_ <- 1 until 10) d.appendBlock(TxHelpers.transfer(TxHelpers.defaultSigner, address))
+    for (_ <- 1 until 10) domain.appendBlock(TxHelpers.transfer(richAccount, address))
 
-    Get(routePath(s"/balance/$address/10")) ~> route ~> check {
-      responseAs[JsObject] shouldBe Json.obj("error" -> 199, "message" -> "Unable to get balance past height 5")
+    val height        = domain.blockchain.height
+    val minimumHeight = height - MaxBalanceDepth
+
+    Get(routePath(s"/balance/$address/${MaxBalanceDepth + 1}")) ~> route ~> check {
+      responseAs[JsObject] shouldBe Json.obj("error" -> 199, "message" -> s"Unable to get balance past height $minimumHeight")
     }
 
     Get(routePath(s"/balance?address=$address&height=1")) ~> route ~> check {
-      responseAs[JsObject] shouldBe Json.obj("error" -> 199, "message" -> "Unable to get balance past height 5")
+      responseAs[JsObject] shouldBe Json.obj("error" -> 199, "message" -> s"Unable to get balance past height $minimumHeight")
     }
   }
 
-  routePath("/balance") in withDomain(balances = Seq(AddrWithBalance(TxHelpers.defaultAddress))) { d =>
-    val route =
-      addressApiRoute
-        .copy(
-          blockchain = d.blockchainUpdater,
-          commonAccountsApi = CommonAccountsApi(
-            () => d.blockchainUpdater.snapshotBlockchain,
-            d.rdb,
-            d.blockchainUpdater
-          )
-        )
-        .route
-    val address       = TxHelpers.signer(1).toAddress
-    val transferCount = 5
-
-    val issue = TxHelpers.issue(TxHelpers.defaultSigner)
-    d.appendBlock(issue)
-
-    for (_ <- 1 until transferCount)
-      d.appendBlock(
-        TxHelpers.transfer(TxHelpers.defaultSigner, address, amount = 1),
-        TxHelpers.transfer(TxHelpers.defaultSigner, address, asset = issue.asset, amount = 2)
+  routePath("/balance") in {
+    val address       = TxHelpers.address(0xaaff01)
+    val transferCount = 4
+
+    val issue = TxHelpers.issue(richAccount)
+    domain.appendBlock(issue)
+
+    for (_ <- 1 to transferCount)
+      domain.appendBlock(
+        TxHelpers.transfer(richAccount, address, amount = 1),
+        TxHelpers.transfer(richAccount, address, asset = issue.asset, amount = 2)
       )
 
-    Get(routePath(s"/balance?address=$address&height=$transferCount")) ~> route ~> check {
-      responseAs[JsValue] shouldBe Json.arr(Json.obj("id" -> address.toString, "balance" -> (transferCount - 2)))
+    val balanceCheckHeight = domain.blockchain.height
+
+    Get(routePath(s"/balance?address=$address&height=$balanceCheckHeight")) ~> route ~> check {
+      responseAs[JsValue] shouldBe Json.arr(Json.obj("id" -> address.toString, "balance" -> transferCount))
     }
-    Post(routePath(s"/balance"), Json.obj("height" -> transferCount, "addresses" -> Seq(address.toString))) ~> route ~> check {
-      responseAs[JsValue] shouldBe Json.arr(Json.obj("id" -> address.toString, "balance" -> (transferCount - 2)))
+    Post(routePath(s"/balance"), Json.obj("height" -> balanceCheckHeight, "addresses" -> Seq(address.toString))) ~> route ~> check {
+      responseAs[JsValue] shouldBe Json.arr(Json.obj("id" -> address.toString, "balance" -> transferCount))
     }
 
-    Get(routePath(s"/balance?address=$address&height=$transferCount&asset=${issue.assetId}")) ~> route ~> check {
-      responseAs[JsValue] shouldBe Json.arr(Json.obj("id" -> address.toString, "balance" -> 2 * (transferCount - 2)))
+    Get(routePath(s"/balance?address=$address&height=$balanceCheckHeight&asset=${issue.assetId}")) ~> route ~> check {
+      responseAs[JsValue] shouldBe Json.arr(Json.obj("id" -> address.toString, "balance" -> 2 * transferCount))
     }
     Post(
       routePath(s"/balance"),
-      Json.obj("height" -> transferCount, "addresses" -> Seq(address.toString), "asset" -> issue.assetId)
+      Json.obj("height" -> balanceCheckHeight, "addresses" -> Seq(address.toString), "asset" -> issue.assetId)
     ) ~> route ~> check {
-      responseAs[JsValue] shouldBe Json.arr(Json.obj("id" -> address.toString, "balance" -> 2 * (transferCount - 2)))
+      responseAs[JsValue] shouldBe Json.arr(Json.obj("id" -> address.toString, "balance" -> 2 * transferCount))
     }
   }
 
@@ -205,31 +183,34 @@ class AddressRouteSpec extends RouteSpec("/addresses") with PathMockFactory with
     }
   }
 
-  routePath(s"/scriptInfo/${allAddresses(1)}") in {
-    val script = ExprScript(TRUE).explicitGet()
+  routePath(s"/scriptInfo/{address}") in {
+    val script = TestCompiler(V5).compileExpression("""
+      sigVerify(base58'', base58'', base58'') ||
+      sigVerify(base58'', base58'', base58'')
+    """)
 
-    (commonAccountApi.script _).expects(allAccounts(1).toAddress).returning(Some(AccountScriptInfo(allAccounts(1).publicKey, script, 123L))).once()
-    (blockchain.accountScript _).when(allAccounts(1).toAddress).returns(Some(AccountScriptInfo(allAccounts(1).publicKey, script, 123L))).once()
-    (blockchain.hasAccountScript _).when(allAccounts(1).toAddress).returns(true).once()
+    val exprScriptOwner = TxHelpers.signer(0xffaa88)
 
-    Get(routePath(s"/scriptInfo/${allAddresses(1)}")) ~> route ~> check {
+    domain.appendBlock(
+      TxHelpers.transfer(richAccount, exprScriptOwner.toAddress),
+      TxHelpers.setScript(exprScriptOwner, script)
+    )
+
+    Get(routePath(s"/scriptInfo/${exprScriptOwner.toAddress}")) ~> route ~> check {
       val response = responseAs[JsObject]
-      (response \ "address").as[String] shouldBe allAddresses(1).toString
-      (response \ "script").as[String] shouldBe "base64:AQa3b8tH"
-      (response \ "scriptText").as[String] shouldBe "true"
-      (response \ "version").as[Int] shouldBe 1
-      (response \ "complexity").as[Long] shouldBe 123
+      (response \ "address").as[String] shouldBe exprScriptOwner.toAddress.toString
+      (response \ "script").as[String] shouldBe "base64:BQMJAAH0AAAAAwEAAAAAAQAAAAABAAAAAAYJAAH0AAAAAwEAAAAAAQAAAAABAAAAAHBPrxY="
+      (response \ "scriptText").as[String] shouldBe "IF(FUNCTION_CALL(Native(500),List(, , )),true,FUNCTION_CALL(Native(500),List(, , )))"
+      (response \ "version").as[Int] shouldBe 5
+      (response \ "complexity").as[Long] shouldBe 400
       (response \ "extraFee").as[Long] shouldBe FeeValidation.ScriptExtraFee
-      (response \ "publicKey").as[String] shouldBe allAccounts(1).publicKey.toString
+      (response \ "publicKey").as[String] shouldBe exprScriptOwner.publicKey.toString
     }
 
-    (commonAccountApi.script _).expects(allAccounts(2).toAddress).returning(None).once()
-    (blockchain.accountScript _).when(allAccounts(2).toAddress).returns(None).once()
-    (blockchain.hasAccountScript _).when(allAccounts(2).toAddress).returns(false).once()
-
-    Get(routePath(s"/scriptInfo/${allAddresses(2)}")) ~> route ~> check {
+    val nonScriptedAddress = TxHelpers.address(0xffaa89)
+    Get(routePath(s"/scriptInfo/$nonScriptedAddress")) ~> route ~> check {
       val response = responseAs[JsObject]
-      (response \ "address").as[String] shouldBe allAddresses(2).toString
+      (response \ "address").as[String] shouldBe nonScriptedAddress.toString
       (response \ "script").asOpt[String] shouldBe None
       (response \ "scriptText").asOpt[String] shouldBe None
       (response \ "version").asOpt[Int] shouldBe None
@@ -238,61 +219,44 @@ class AddressRouteSpec extends RouteSpec("/addresses") with PathMockFactory with
       (response \ "publicKey").asOpt[String] shouldBe None
     }
 
-    val contractWithMeta = DApp(
-      meta = DAppMeta(
-        version = 1,
-        List(
-          CallableFuncSignature(ByteString.copyFrom(Array[Byte](1, 2, 3))),
-          CallableFuncSignature(ByteString.copyFrom(Array[Byte](8))),
-          CallableFuncSignature(ByteString.EMPTY)
-        )
-      ),
-      decs = List(),
-      callableFuncs = List(
-        CallableFunction(
-          CallableAnnotation("i"),
-          FUNC("call1", List("a", "b", "c"), CONST_BOOLEAN(true))
-        ),
-        CallableFunction(
-          CallableAnnotation("i"),
-          FUNC("call2", List("d"), CONST_BOOLEAN(true))
-        ),
-        CallableFunction(
-          CallableAnnotation("i"),
-          FUNC("call3", Nil, CONST_BOOLEAN(true))
-        )
-      ),
-      verifierFuncOpt = Some(VerifierFunction(VerifierAnnotation("t"), FUNC("verify", List(), TRUE)))
+    val contractWithMeta = TestCompiler(V5).compileContract("""
+      @Callable(i)
+      func call1(a: Int, b: ByteVector, c: ByteVector|Int) = []
+
+      @Callable(i)
+      func call2(d: String) = []
+
+      @Callable(i)
+      func call3() = []
+
+      @Verifier(tx)
+      func check() = sigVerify(base58'', base58'', base58'') || sigVerify(base58'', base58'', base58'')
+    """)
+
+    val dappOwner = TxHelpers.signer(0xffaa90)
+
+    domain.appendBlock(
+      TxHelpers.transfer(richAccount, dappOwner.toAddress),
+      TxHelpers.setScript(dappOwner, contractWithMeta)
     )
 
-    val contractScript       = ContractScript(V3, contractWithMeta).explicitGet()
-    val callableComplexities = Map("a" -> 1L, "b" -> 2L, "c" -> 3L, "d" -> 100L, "verify" -> 11L)
-    (commonAccountApi.script _)
-      .expects(allAccounts(3).toAddress)
-      .returning(Some(AccountScriptInfo(allAccounts(3).publicKey, contractScript, 11L)))
-      .once()
-    (blockchain.accountScript _)
-      .when(allAccounts(3).toAddress)
-      .returns(Some(AccountScriptInfo(allAccounts(3).publicKey, contractScript, 11L, complexitiesByEstimator = Map(1 -> callableComplexities))))
-    (blockchain.hasAccountScript _).when(allAccounts(3).toAddress).returns(true).once()
-
-    Get(routePath(s"/scriptInfo/${allAddresses(3)}")) ~> route ~> check {
+    Get(routePath(s"/scriptInfo/${dappOwner.toAddress}")) ~> route ~> check {
       val response = responseAs[JsObject]
-      (response \ "address").as[String] shouldBe allAddresses(3).toString
+      (response \ "address").as[String] shouldBe dappOwner.toAddress.toString
       (response \ "script").as[String] should fullyMatch regex "base64:.+".r
       (response \ "scriptText").as[String] should fullyMatch regex "DApp\\(.+\\)".r
-      (response \ "version").as[Int] shouldBe 3
-      (response \ "complexity").as[Long] shouldBe 100
-      (response \ "verifierComplexity").as[Long] shouldBe 11
-      (response \ "callableComplexities").as[Map[String, Long]] shouldBe callableComplexities - "verify"
+      (response \ "version").as[Int] shouldBe 5
+      (response \ "complexity").as[Long] shouldBe 400
+      (response \ "verifierComplexity").as[Long] shouldBe 400
+      (response \ "callableComplexities").as[Map[String, Long]] shouldBe Map("call1" -> 1, "call2" -> 1, "call3" -> 1)
       (response \ "extraFee").as[Long] shouldBe FeeValidation.ScriptExtraFee
-      (response \ "publicKey").as[String] shouldBe allAccounts(3).publicKey.toString
+      (response \ "publicKey").as[String] shouldBe dappOwner.publicKey.toString
     }
 
-    Get(routePath(s"/scriptInfo/${allAddresses(3)}/meta")) ~> route ~> check {
+    Get(routePath(s"/scriptInfo/${dappOwner.toAddress}/meta")) ~> route ~> check {
       val response = responseAs[JsObject]
-      (response \ "address").as[String] shouldBe allAddresses(3).toString
-      (response \ "meta" \ "version").as[String] shouldBe "1"
+      (response \ "address").as[String] shouldBe dappOwner.toAddress.toString
+      (response \ "meta" \ "version").as[String] shouldBe "2"
       (response \ "meta" \ "callableFuncTypes" \ "call1" \ 0 \ "name").as[String] shouldBe "a"
       (response \ "meta" \ "callableFuncTypes" \ "call1" \ 0 \ "type").as[String] shouldBe "Int"
       (response \ "meta" \ "callableFuncTypes" \ "call1" \ 1 \ "name").as[String] shouldBe "b"
@@ -304,105 +268,66 @@ class AddressRouteSpec extends RouteSpec("/addresses") with PathMockFactory with
       (response \ "meta" \ "callableFuncTypes" \ "call3").as[JsArray] shouldBe JsArray()
     }
 
-    val contractWithoutMeta = contractWithMeta.copy(meta = DAppMeta())
-    (blockchain.accountScript _)
-      .when(allAccounts(4).toAddress)
-      .onCall((_: Address) => Some(AccountScriptInfo(allAccounts(4).publicKey, ContractScript(V3, contractWithoutMeta).explicitGet(), 11L)))
+    val dappWoMetaOwner     = TxHelpers.signer(0xffaa91)
+    val contractWithoutMeta = contractWithMeta.copy(expr = contractWithMeta.expr.copy(meta = DAppMeta()))
+    domain.appendBlock(
+      TxHelpers.transfer(richAccount, dappWoMetaOwner.toAddress),
+      TxHelpers.setScript(dappWoMetaOwner, contractWithoutMeta)
+    )
 
-    Get(routePath(s"/scriptInfo/${allAddresses(4)}/meta")) ~> route ~> check {
+    Get(routePath(s"/scriptInfo/${dappWoMetaOwner.toAddress}/meta")) ~> route ~> check {
       val response = responseAs[JsObject]
-      (response \ "address").as[String] shouldBe allAddresses(4).toString
+      (response \ "address").as[String] shouldBe dappWoMetaOwner.toAddress.toString
       (response \ "meta" \ "version").as[String] shouldBe "0"
     }
 
-    (blockchain.accountScript _)
-      .when(allAccounts(5).toAddress)
-      .onCall { (_: Address) =>
-        Thread.sleep(100000)
-        None
-      }
-
-    implicit val routeTestTimeout = RouteTestTimeout(10.seconds)
-    implicit val timeout          = routeTestTimeout.duration
-    Get(routePath(s"/scriptInfo/${allAddresses(5)}")) ~> route ~> check {
-      val json = responseAs[JsValue]
-      (json \ "message").as[String] shouldBe "The request took too long to complete"
-    }
-
-    val contractWithoutVerifier             = contractWithMeta.copy(verifierFuncOpt = None)
-    val contractWithoutVerifierComplexities = Map("a" -> 1L, "b" -> 2L, "c" -> 3L)
-    (blockchain.accountScript _)
-      .when(allAccounts(6).toAddress)
-      .onCall((_: Address) =>
-        Some(
-          AccountScriptInfo(
-            allAccounts(6).publicKey,
-            ContractScript(V3, contractWithoutVerifier).explicitGet(),
-            0L,
-            complexitiesByEstimator = Map(1 -> contractWithoutVerifierComplexities)
-          )
-        )
-      )
-    (blockchain.hasAccountScript _).when(allAccounts(6).toAddress).returns(true).once()
+    val dappWoVerifierOwner     = TxHelpers.signer(0xffaa92)
+    val contractWithoutVerifier = contractWithMeta.copy(expr = contractWithMeta.expr.copy(verifierFuncOpt = None))
+    domain.appendBlock(
+      TxHelpers.transfer(richAccount, dappWoVerifierOwner.toAddress),
+      TxHelpers.setScript(dappWoVerifierOwner, contractWithoutVerifier)
+    )
+    val contractWithoutVerifierComplexities = Map("call1" -> 1L, "call2" -> 1L, "call3" -> 1L)
 
-    Get(routePath(s"/scriptInfo/${allAddresses(6)}")) ~> route ~> check {
+    Get(routePath(s"/scriptInfo/${dappWoVerifierOwner.toAddress}")) ~> route ~> check {
       val response = responseAs[JsObject]
-      (response \ "address").as[String] shouldBe allAddresses(6).toString
-      (response \ "version").as[Int] shouldBe 3
-      (response \ "complexity").as[Long] shouldBe 3
+      (response \ "address").as[String] shouldBe dappWoVerifierOwner.toAddress.toString
+      (response \ "version").as[Int] shouldBe 5
+      (response \ "complexity").as[Long] shouldBe 1
       (response \ "verifierComplexity").as[Long] shouldBe 0
       (response \ "callableComplexities").as[Map[String, Long]] shouldBe contractWithoutVerifierComplexities
-      (response \ "extraFee").as[Long] shouldBe FeeValidation.ScriptExtraFee
-      (response \ "publicKey").as[String] shouldBe allAccounts(6).publicKey.toString
+      (response \ "extraFee").as[Long] shouldBe 0
+      (response \ "publicKey").as[String] shouldBe dappWoVerifierOwner.publicKey.toString
     }
   }
 
   routePath(s"/scriptInfo/ after ${BlockchainFeatures.SynchronousCalls}") in {
-    val blockchain = stub[Blockchain]("blockchain")
-    val route      = seal(addressApiRoute.copy(blockchain = blockchain).route)
-    (() => blockchain.activatedFeatures).when().returning(Map(BlockchainFeatures.SynchronousCalls.id -> 0))
-
-    val script                            = ExprScript(TRUE).explicitGet()
-    def info(complexity: Int, index: Int) = Some(AccountScriptInfo(allAccounts(index).publicKey, script, complexity))
+    val simpleScript = TestCompiler(V6).compileExpression("""
+      sigVerify_32Kb(base58'', base58'', base58'')
+    """)
 
-    (blockchain.accountScript _).when(allAddresses(1)).returns(info(201, 1))
-    Get(routePath(s"/scriptInfo/${allAddresses(1)}")) ~> route ~> check {
-      val response = responseAs[JsObject]
-      (response \ "address").as[String] shouldBe allAddresses(1).toString
-      (response \ "version").as[Int] shouldBe 1
-      (response \ "complexity").as[Long] shouldBe 201
-      (response \ "verifierComplexity").as[Long] shouldBe 201
-      (response \ "extraFee").as[Long] shouldBe FeeValidation.ScriptExtraFee
-      (response \ "publicKey").as[String] shouldBe allAccounts(1).publicKey.toString
-    }
+    val noExtraFeeOwner = TxHelpers.signer(0xffaa95)
 
-    (blockchain.accountScript _).when(allAddresses(2)).returns(info(199, 2))
-    Get(routePath(s"/scriptInfo/${allAddresses(2)}")) ~> route ~> check {
-      val response = responseAs[JsObject]
-      (response \ "address").as[String] shouldBe allAddresses(2).toString
-      (response \ "version").as[Int] shouldBe 1
-      (response \ "complexity").as[Long] shouldBe 199
-      (response \ "verifierComplexity").as[Long] shouldBe 199
-      (response \ "extraFee").as[Long] shouldBe 0
-      (response \ "publicKey").as[String] shouldBe allAccounts(2).publicKey.toString
-    }
+    domain.appendBlock(
+      TxHelpers.transfer(richAccount, noExtraFeeOwner.toAddress),
+      TxHelpers.setScript(noExtraFeeOwner, simpleScript)
+    )
 
-    (blockchain.accountScript _).when(allAddresses(3)).returns(None)
-    Get(routePath(s"/scriptInfo/${allAddresses(3)}")) ~> route ~> check {
+    Get(routePath(s"/scriptInfo/${noExtraFeeOwner.toAddress}")) ~> route ~> check {
       val response = responseAs[JsObject]
-      (response \ "address").as[String] shouldBe allAddresses(3).toString
-      (response \ "version").asOpt[Int] shouldBe None
-      (response \ "complexity").as[Long] shouldBe 0
-      (response \ "verifierComplexity").as[Long] shouldBe 0
+      (response \ "address").as[String] shouldBe noExtraFeeOwner.toAddress.toString
+      (response \ "version").as[Int] shouldBe 6
+      (response \ "complexity").as[Long] shouldBe 64
+      (response \ "verifierComplexity").as[Long] shouldBe 64
       (response \ "extraFee").as[Long] shouldBe 0
-      (response \ "publicKey").asOpt[String] shouldBe None
+      (response \ "publicKey").as[String] shouldBe noExtraFeeOwner.publicKey.toString
     }
   }
 
-  routePath(s"/data/${allAddresses(1)}?matches=regex") in {
+  routePath(s"/data/{address}?matches=regex") in {
     val invalidRegexps = List("[a-z", "([a-z]{0}", "[a-z]{0", "[a-z]{,5}")
     for (regex <- invalidRegexps) {
-      Get(routePath(s"""/data/${allAddresses(1)}?matches=$regex""")) ~> route ~> check {
+      Get(routePath(s"""/data/${richAccount.toAddress}?matches=$regex""")) ~> route ~> check {
         responseAs[String] should include("Cannot compile regex")
       }
     }
@@ -411,39 +336,25 @@ class AddressRouteSpec extends RouteSpec("/addresses") with PathMockFactory with
   routePath(s"/data/{address} with Transfer-Encoding: chunked") in {
     val account = TxHelpers.signer(1)
 
-    withDomain(DomainPresets.RideV5, balances = AddrWithBalance.enoughBalances(account)) { d =>
-      d.appendBlock(TxHelpers.dataSingle(account))
-
-      val route =
-        addressApiRoute
-          .copy(
-            blockchain = d.blockchainUpdater,
-            commonAccountsApi = CommonAccountsApi(
-              () => d.blockchainUpdater.snapshotBlockchain,
-              d.rdb,
-              d.blockchainUpdater
-            )
-          )
-          .route
-
-      val requestBody = Json.obj("keys" -> Seq("test"))
-
-      val headers: Seq[HttpHeader] =
-        Seq(`Transfer-Encoding`(TransferEncodings.chunked), `Content-Type`(ContentTypes.`application/json`), Accept(MediaTypes.`application/json`))
-
-      Post(
-        routePath(s"/data/${account.toAddress}"),
-        HttpEntity.Chunked(ContentTypes.`application/json`, Source(Seq(Chunk(akka.util.ByteString.fromString(requestBody.toString)), LastChunk)))
-      ).withHeaders(headers) ~> route ~> check {
-        responseAs[JsValue] should matchJson("""[{"key":"test","type":"string","value":"test"}]""")
-      }
+    domain.appendBlock(TxHelpers.dataSingle(account))
+
+    val requestBody = Json.obj("keys" -> Seq("test"))
+
+    val headers: Seq[HttpHeader] =
+      Seq(`Transfer-Encoding`(TransferEncodings.chunked), `Content-Type`(ContentTypes.`application/json`), Accept(MediaTypes.`application/json`))
+
+    Post(
+      routePath(s"/data/${account.toAddress}"),
+      HttpEntity.Chunked(ContentTypes.`application/json`, Source(Seq(Chunk(akka.util.ByteString.fromString(requestBody.toString)), LastChunk)))
+    ).withHeaders(headers) ~> route ~> check {
+      responseAs[JsValue] should matchJson("""[{"key":"test","type":"string","value":"test"}]""")
     }
   }
 
   routePath(s"/data/{address} - handles keys limit") in {
     def checkErrorResponse(): Unit = {
       response.status shouldBe StatusCodes.BadRequest
-      (responseAs[JsObject] \ "message").as[String] shouldBe TooBigArrayAllocation(addressApiRoute.settings.dataKeysRequestLimit).message
+      (responseAs[JsObject] \ "message").as[String] shouldBe TooBigArrayAllocation(restAPISettings.dataKeysRequestLimit).message
     }
 
     def checkResponse(key: String, value: String, idsCount: Int): Unit = {
@@ -466,47 +377,33 @@ class AddressRouteSpec extends RouteSpec("/addresses") with PathMockFactory with
     val key     = "testKey"
     val value   = "testValue"
 
-    withDomain(DomainPresets.RideV5, balances = AddrWithBalance.enoughBalances(account)) { d =>
-      d.appendBlock(TxHelpers.dataSingle(account, key = key, value = value))
-
-      val route =
-        addressApiRoute
-          .copy(
-            blockchain = d.blockchainUpdater,
-            commonAccountsApi = CommonAccountsApi(
-              () => d.blockchainUpdater.snapshotBlockchain,
-              d.rdb,
-              d.blockchainUpdater
-            )
-          )
-          .route
-
-      val maxLimitKeys      = Seq.fill(addressApiRoute.settings.dataKeysRequestLimit)(key)
-      val moreThanLimitKeys = key +: maxLimitKeys
-
-      Get(routePath(s"/data/${account.toAddress}?${maxLimitKeys.map("key=" + _).mkString("&")}")) ~> route ~> check(
-        checkResponse(key, value, maxLimitKeys.size)
-      )
-      Get(routePath(s"/data/${account.toAddress}?${moreThanLimitKeys.map("key=" + _).mkString("&")}")) ~> route ~> check(
-        checkErrorResponse()
-      )
+    domain.appendBlock(TxHelpers.dataSingle(account, key = key, value = value))
 
-      Post(routePath(s"/data/${account.toAddress}"), FormData(maxLimitKeys.map("key" -> _)*)) ~> route ~> check(
-        checkResponse(key, value, maxLimitKeys.size)
-      )
-      Post(routePath(s"/data/${account.toAddress}"), FormData(moreThanLimitKeys.map("key" -> _)*)) ~> route ~> check(
-        checkErrorResponse()
-      )
+    val maxLimitKeys      = Seq.fill(restAPISettings.dataKeysRequestLimit)(key)
+    val moreThanLimitKeys = key +: maxLimitKeys
 
-      Post(
-        routePath(s"/data/${account.toAddress}"),
-        HttpEntity(ContentTypes.`application/json`, Json.obj("keys" -> Json.arr(maxLimitKeys.map(key => key: JsValueWrapper)*)).toString())
-      ) ~> route ~> check(checkResponse(key, value, maxLimitKeys.size))
-      Post(
-        routePath(s"/data/${account.toAddress}"),
-        HttpEntity(ContentTypes.`application/json`, Json.obj("keys" -> Json.arr(moreThanLimitKeys.map(key => key: JsValueWrapper)*)).toString())
-      ) ~> route ~> check(checkErrorResponse())
-    }
+    Get(routePath(s"/data/${account.toAddress}?${maxLimitKeys.map("key=" + _).mkString("&")}")) ~> route ~> check(
+      checkResponse(key, value, maxLimitKeys.size)
+    )
+    Get(routePath(s"/data/${account.toAddress}?${moreThanLimitKeys.map("key=" + _).mkString("&")}")) ~> route ~> check(
+      checkErrorResponse()
+    )
+
+    Post(routePath(s"/data/${account.toAddress}"), FormData(maxLimitKeys.map("key" -> _)*)) ~> route ~> check(
+      checkResponse(key, value, maxLimitKeys.size)
+    )
+    Post(routePath(s"/data/${account.toAddress}"), FormData(moreThanLimitKeys.map("key" -> _)*)) ~> route ~> check(
+      checkErrorResponse()
+    )
+
+    Post(
+      routePath(s"/data/${account.toAddress}"),
+      HttpEntity(ContentTypes.`application/json`, Json.obj("keys" -> Json.arr(maxLimitKeys.map(key => key: JsValueWrapper)*)).toString())
+    ) ~> route ~> check(checkResponse(key, value, maxLimitKeys.size))
+    Post(
+      routePath(s"/data/${account.toAddress}"),
+      HttpEntity(ContentTypes.`application/json`, Json.obj("keys" -> Json.arr(moreThanLimitKeys.map(key => key: JsValueWrapper)*)).toString())
+    ) ~> route ~> check(checkErrorResponse())
   }
 
   routePath(s"/data/{address} - handles empty keys input in POST") in {
@@ -524,4 +421,20 @@ class AddressRouteSpec extends RouteSpec("/addresses") with PathMockFactory with
       HttpEntity(ContentTypes.`application/json`, Json.obj("keys" -> JsArray.empty).toString())
     ) ~> route ~> check(checkErrorResponse())
   }
+
+  "handles stack overflow" in {
+    import monix.execution.Scheduler.Implicits.global
+    val dataOwner        = TxHelpers.signer(0xaaff05)
+    val dataTransactions = (1 to 500) map { d => TxHelpers.data(dataOwner, Seq.tabulate(100)(i => IntegerDataEntry(s"k_${d}_$i", i))) }
+
+    domain.appendBlock(TxHelpers.transfer(richAccount, dataOwner.toAddress, 100.waves))
+    domain.appendBlock(dataTransactions*)
+    domain.appendBlock()
+
+    domain.accountsApi
+      .dataStream(dataOwner.toAddress, Some("nomatch"))
+      .toListL
+      .runSyncUnsafe(15.seconds) should be(empty)
+
+  }
 }
```
