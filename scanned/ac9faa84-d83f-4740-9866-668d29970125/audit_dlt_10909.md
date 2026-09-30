# [?] NODE-1455: Fix Transfer overflow check (#2085)

## Summary
Severity: Unknown
Chain: Waves
Component: wavesplatform/Waves
Published: 2019-03-25
Source: https://github.com/wavesplatform/Waves/commit/e9498e173cce319eacd9858d0ce1b491bc781726
Type: security-commit

## Details
NODE-1455: Fix Transfer overflow check (#2085)

## Patch
### src/main/scala/com/wavesplatform/state/diffs/TransferTransactionDiff.scala
```diff
@@ -9,6 +9,7 @@ import com.wavesplatform.transaction.Asset.{IssuedAsset, Waves}
 import com.wavesplatform.transaction.ValidationError
 import com.wavesplatform.transaction.ValidationError.GenericError
 import com.wavesplatform.transaction.transfer._
+import com.wavesplatform.features.FeatureProvider._
 
 import scala.util.{Right, Try}
 
@@ -73,7 +74,7 @@ object TransferTransactionDiff {
   }
 
   private def validateOverflow(blockchain: Blockchain, tx: TransferTransaction) = {
-    if (blockchain.activatedFeatures.contains(BlockchainFeatures.Ride4DApps.id)) {
+    if (blockchain.isFeatureActivated(BlockchainFeatures.Ride4DApps, blockchain.height)) {
       Right(()) // lets transaction validates itself
     } else {
       Try(Math.addExact(tx.fee, tx.amount))
```

### src/test/scala/com/wavesplatform/state/diffs/TransferTransactionDiffTest.scala
```diff
@@ -3,13 +3,15 @@ package com.wavesplatform.state.diffs
 import cats.implicits._
 import com.wavesplatform.account.Address
 import com.wavesplatform.common.utils.EitherExt2
+import com.wavesplatform.features.BlockchainFeatures
 import com.wavesplatform.lagonaki.mocks.TestBlock
+import com.wavesplatform.settings.TestFunctionalitySettings
 import com.wavesplatform.state.{LeaseBalance, Portfolio}
 import com.wavesplatform.transaction.Asset.{IssuedAsset, Waves}
 import com.wavesplatform.transaction.ValidationError.GenericError
 import com.wavesplatform.transaction.assets._
 import com.wavesplatform.transaction.transfer._
-import com.wavesplatform.transaction.{Asset, GenesisTransaction}
+import com.wavesplatform.transaction.{Asset, GenesisTransaction, ValidationError}
 import com.wavesplatform.{NoShrink, TransactionGen}
 import org.scalacheck.Gen
 import org.scalatest.{Matchers, PropSpec}
@@ -65,6 +67,38 @@ class TransferTransactionDiffTest extends PropSpec with PropertyChecks with Matc
     } yield (genesis, issue, feeIssue, transfer)
   }
 
+  property("handle transactions with amount + fee > Long.MaxValue") {
+    val precs = for {
+      master    <- accountGen
+      recepient <- otherAccountGen(candidate = master)
+      ts        <- positiveIntGen
+      genesis: GenesisTransaction = GenesisTransaction.create(master, ENOUGH_AMT, ts).explicitGet()
+      issue: IssueTransaction <- issueReissueBurnGeneratorP(Long.MaxValue, master).map(_._1)
+      asset    = IssuedAsset(issue.id())
+      transfer = TransferTransactionV1.selfSigned(asset, master, recepient, Long.MaxValue, ts, Waves, 100000, Array.emptyByteArray).explicitGet()
+    } yield (genesis, issue, transfer)
+
+    val rdEnabled = TestFunctionalitySettings.Stub
+
+    val rdDisabled = rdEnabled.copy(
+      preActivatedFeatures = Map(
+        BlockchainFeatures.SmartAccounts.id -> 0,
+        BlockchainFeatures.SmartAssets.id   -> 0,
+        BlockchainFeatures.FairPoS.id       -> 0
+      ))
+
+    forAll(precs) {
+      case (genesis, issue, transfer) =>
+        assertDiffEi(Seq(TestBlock.create(Seq(genesis, issue))), TestBlock.create(Seq(transfer)), rdEnabled) { diffEi =>
+          diffEi shouldBe an[Right[_, _]]
+        }
+
+        assertDiffEi(Seq(TestBlock.create(Seq(genesis, issue))), TestBlock.create(Seq(transfer)), rdDisabled) { diffEi =>
+          diffEi shouldBe Left(TransactionDiffer.TransactionValidationError(ValidationError.OverflowError, transfer))
+        }
+    }
+  }
+
   property("fails, if smart asset used as a fee") {
     import smart._
 
```
